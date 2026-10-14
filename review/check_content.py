#!/usr/bin/env python3
"""Check briefs, manifests, drafts, scripts and referenced evidence.

Blocking errors (passed=false): missing artifacts; fewer than three distinct pieces;
unresolvable claim markers or evidence (unknown item, wrong version, missing quote or
segment, not in the evidence store); evidence outside the run's date window; fewer
than three independent publishers behind a piece; any input kind absent from the
cited evidence across the series; a script citing claims its article does not make.
Warnings: length targets, uncited claims, manifest drift, single-perspective pieces,
repaired quotes, and the standing reminder that interpretation needs human review.

review_id fingerprints the as-of date, the briefs, every draft and script, the
manifests, every evidence reference and the retained asset files they point to.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import abs_path, markers_in, read_jsonl, resolve_evidence  # noqa: E402
from lib.receipt import Receipt  # noqa: E402

STAGE = "check_content"
WINDOW_DAYS = 30
PIECES = ("01", "02", "03")
KINDS = ("feed", "youtube", "podcast")
ARTICLE_WORDS = (600, 900)
NARRATION_WORDS = (450, 750)


def sha_file(path: str) -> str | None:
    p = abs_path(path)
    if not p or not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


def article_body(md: str) -> str:
    body = md.split("\n## Sources", 1)[0]
    return re.sub(r"^#.*$", "", body, count=1, flags=re.M)


def narration(md: str) -> str:
    out = []
    for line in md.split("\n## Description", 1)[0].splitlines():
        s = line.strip()
        if s.lower().startswith(("narration:", "**narration:**", "- narration:")):
            out.append(re.sub(r"^\W*narration:\**\s*", "", s, flags=re.I))
    return " ".join(out)


def ngrams(text: str, n: int = 5) -> set:
    toks = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1))}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    try:
        from dateutil import parser as dp
        d = dp.isoparse(value)
    except (ValueError, TypeError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=_dt.timezone.utc)
    return d.astimezone(_dt.timezone.utc).date()


def main(run_dir: str) -> int:
    receipt = Receipt(run_dir, STAGE, tools=["python"])
    issues = []

    def err(message, piece_id=None, artifact=None):
        issues.append({"piece_id": piece_id, "artifact": artifact, "severity": "error", "message": message})

    def warn(message, piece_id=None, artifact=None):
        issues.append({"piece_id": piece_id, "artifact": artifact, "severity": "warning", "message": message})

    run = json.load(open(os.path.join(run_dir, "run.json"), encoding="utf-8"))
    as_of = _dt.date.fromisoformat(run["as_of_date"])
    start = as_of - _dt.timedelta(days=WINDOW_DAYS - 1)

    def load(name, required=True):
        p = os.path.join(run_dir, name)
        if not os.path.exists(p):
            if required:
                err(f"required artifact missing: {name}", artifact=p)
            return []
        try:
            return read_jsonl(p)
        except (json.JSONDecodeError, OSError) as exc:
            err(f"{name} is not valid JSONL: {exc}", artifact=p)
            return []

    briefs = {b.get("piece_id"): b for b in load("briefs.jsonl")}
    art_manifests = {m.get("piece_id"): m for m in load("articles.jsonl")}
    scr_manifests = {m.get("piece_id"): m for m in load("video_scripts.jsonl")}
    eligible = {it["item_id"]: it for it in load("eligible.jsonl")}
    decisions = {d["item_id"]: d for d in load("decisions.jsonl")}

    # ---- store view (through the interface)
    store_latest = {}
    proc = subprocess.run(["bash", "data/store.sh", "list"], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            if line.strip():
                r = json.loads(line)
                store_latest[r["item_id"]] = r["version_id"]
    else:
        err(f"evidence store unavailable: {proc.stderr.strip()[:200]}")

    def in_store(item_id, version_id):
        if store_latest.get(item_id) == version_id:
            return True
        p = subprocess.run(["bash", "data/store.sh", "get", item_id, version_id], cwd=ROOT, capture_output=True, text=True)
        return p.returncode == 0

    # ---- pieces, drafts, markers
    texts, scripts, cited_claims, stats = {}, {}, {}, {"evidence_refs": 0, "publishers_per_piece": {}, "kinds_cited": [],
                                                       "article_words": {}, "narration_words": {}, "perspectives_per_piece": {}}
    for pid in PIECES:
        b = briefs.get(pid)
        if not b:
            err(f"brief {pid} missing", piece_id=pid)
            continue
        claim_ids = [c.get("claim_id") for c in b.get("claims", [])]
        if len(claim_ids) != len(set(claim_ids)):
            err("duplicate claim ids in brief", piece_id=pid)
        for name, manifests, store_text in (("article", art_manifests, texts), ("video script", scr_manifests, scripts)):
            m = manifests.get(pid)
            if not m:
                err(f"{name} manifest for piece {pid} missing", piece_id=pid)
                continue
            path = m.get("path")
            if not path or not os.path.exists(abs_path(path)):
                err(f"{name} draft missing: {path}", piece_id=pid, artifact=path)
                continue
            md = open(abs_path(path), encoding="utf-8").read()
            store_text[pid] = md
            body = article_body(md) if name == "article" else md.split("\n## Description", 1)[0]
            marks = markers_in(body)
            unknown = [x for x in marks if x not in claim_ids]
            if unknown:
                err(f"{name} cites markers that are not claims of brief {pid}: {unknown}", piece_id=pid, artifact=path)
            own = [x for x in marks if x in claim_ids]
            if name == "article":
                cited_claims[pid] = own
                uncited = [c for c in claim_ids if c not in own]
                if uncited:
                    warn(f"article never cites claims {uncited}", piece_id=pid, artifact=path)
                if not own:
                    err("article cites no claims", piece_id=pid, artifact=path)
                n = words(body)
                stats["article_words"][pid] = n
                if not (ARTICLE_WORDS[0] <= n <= ARTICLE_WORDS[1]):
                    warn(f"article body is {n} words; target {ARTICLE_WORDS[0]}-{ARTICLE_WORDS[1]} excluding sources", piece_id=pid, artifact=path)
                if "AI assistance" not in md and "AI-assisted" not in md:
                    warn("article lacks the AI-assistance disclosure line", piece_id=pid, artifact=path)
                if "## Sources" not in md:
                    err("article has no Sources section resolving its claim markers", piece_id=pid, artifact=path)
            else:
                n = words(re.sub(r"\[\d\d-c\d+\]", "", narration(md)))
                stats["narration_words"][pid] = n
                if not (NARRATION_WORDS[0] <= n <= NARRATION_WORDS[1]):
                    warn(f"narration is {n} words (~{n / 150:.1f} min); target {NARRATION_WORDS[0]}-{NARRATION_WORDS[1]} for 3-5 minutes", piece_id=pid, artifact=path)
                if len(own) < 3:
                    warn(f"script cites only {len(own)} claims", piece_id=pid, artifact=path)
                art_marks = cited_claims.get(pid)
                if art_marks is not None:
                    extra = [x for x in own if x not in art_marks]
                    if extra:
                        err(f"script cites claims the article does not make: {extra}", piece_id=pid, artifact=path)
                if "AI-assisted" not in md and "AI assistance" not in md:
                    warn("script lacks the AI-assistance disclosure line", piece_id=pid, artifact=path)
            manifest_ids = m.get("claim_ids") or []
            if sorted(manifest_ids) != sorted(own):
                warn(f"{name} manifest claim_ids differ from markers in the draft (draft is authoritative)", piece_id=pid, artifact=path)

    # ---- distinctness
    titles = [briefs[p].get("title", "").strip().lower() for p in PIECES if p in briefs]
    if len(titles) != len(set(titles)):
        err("two pieces share a title")
    arg_sets = {p: set(re.findall(r"[a-z0-9']+", briefs[p].get("argument", "").lower())) for p in PIECES if p in briefs}
    body_grams = {p: ngrams(article_body(texts[p])) for p in texts}
    ps = [p for p in PIECES if p in briefs]
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            a, b = ps[i], ps[j]
            if jaccard(arg_sets[a], arg_sets[b]) > 0.6:
                warn(f"arguments of pieces {a} and {b} overlap heavily")
            if a in body_grams and b in body_grams:
                ov = jaccard(body_grams[a], body_grams[b])
                if ov > 0.5:
                    err(f"articles {a} and {b} share {ov:.0%} of their 5-grams; pieces must be distinct")
                elif ov > 0.3:
                    warn(f"articles {a} and {b} share {ov:.0%} of their 5-grams")

    # ---- evidence resolution, versions, dates, independence, kinds
    evidence_refs = []
    kinds_cited = set()
    for pid in PIECES:
        b = briefs.get(pid)
        if not b:
            continue
        pubs, perspectives = set(), set()
        cited = set(cited_claims.get(pid, []))
        for c in b.get("claims", []):
            for ev in c.get("evidence", []):
                stats["evidence_refs"] += 1
                item = eligible.get(ev.get("item_id"))
                loc = ev.get("locator") or {}
                evidence_refs.append([ev.get("item_id"), ev.get("version_id"), json.dumps(loc, sort_keys=True)])
                if not item:
                    err(f"{c.get('claim_id')}: evidence item {ev.get('item_id')} is not in this run's eligible evidence", piece_id=pid)
                    continue
                if ev.get("version_id") != item.get("version_id"):
                    err(f"{c.get('claim_id')}: cites version {str(ev.get('version_id'))[:12]} but the run's evidence version is {str(item.get('version_id'))[:12]}", piece_id=pid)
                d = decisions.get(item["item_id"])
                if not d or d.get("decision") != "accept":
                    err(f"{c.get('claim_id')}: cites {item['item_id']} which was not accepted by editorial selection", piece_id=pid)
                if not in_store(item["item_id"], ev.get("version_id")):
                    err(f"{c.get('claim_id')}: version {str(ev.get('version_id'))[:12]} of {item['item_id']} is not in the evidence store", piece_id=pid)
                res = resolve_evidence(ev, item)
                if not res["ok"]:
                    err(f"{c.get('claim_id')}: {res['problem']} ({item['item_id']})", piece_id=pid)
                pd = parse_date(item.get("published_at"))
                if pd is None:
                    err(f"{c.get('claim_id')}: evidence {item['item_id']} has no valid publication date", piece_id=pid)
                elif not (start <= pd <= as_of):
                    err(f"{c.get('claim_id')}: evidence {item['item_id']} published {pd} is outside the window {start}..{as_of}", piece_id=pid)
                if c.get("claim_id") in cited:
                    pubs.add(item.get("publisher_id"))
                    perspectives.add(item.get("source_perspective") or "unknown")
                    kinds_cited.add(item.get("kind"))
        stats["publishers_per_piece"][pid] = sorted(pubs)
        stats["perspectives_per_piece"][pid] = sorted(perspectives)
        if len(pubs) < 3:
            err(f"piece cites evidence from {len(pubs)} independent publishers; at least three required", piece_id=pid)
        if len(perspectives - {"unknown"}) <= 1 and pubs:
            warn(f"piece rests on a single configured perspective ({', '.join(sorted(perspectives))}); name the missing perspectives", piece_id=pid)
        if b.get("validation", {}).get("quotes_repaired"):
            warn(f"{b['validation']['quotes_repaired']} quote(s) were normalised to the retained wording; verify they still support the claims", piece_id=pid)
        if b.get("dropped_claims"):
            warn(f"{len(b['dropped_claims'])} claim(s) were dropped during brief validation for lack of locatable evidence", piece_id=pid)
        if not (b.get("limitations") or "").strip():
            err("brief has no limitations section", piece_id=pid)
        warn("interpretation, credibility judgements and tone require human review before approval", piece_id=pid)
    stats["kinds_cited"] = sorted(kinds_cited)
    missing_kinds = [k for k in KINDS if k not in kinds_cited]
    if briefs and missing_kinds:
        err(f"cited evidence across the series lacks input kind(s): {missing_kinds}")

    # ---- fingerprint
    fp = {
        "as_of_date": run["as_of_date"],
        "briefs": sha_file(os.path.join(run_dir, "briefs.jsonl")),
        "manifests": {"articles": sha_file(os.path.join(run_dir, "articles.jsonl")), "scripts": sha_file(os.path.join(run_dir, "video_scripts.jsonl"))},
        "articles": {pid: sha_file(art_manifests[pid]["path"]) for pid in art_manifests if art_manifests[pid].get("path")},
        "scripts": {pid: sha_file(scr_manifests[pid]["path"]) for pid in scr_manifests if scr_manifests[pid].get("path")},
        "evidence": sorted({json.dumps(r) for r in evidence_refs}),
        "assets": {},
    }
    for ref in evidence_refs:
        it = eligible.get(ref[0])
        if it:
            for key in ("text_path", "segments_path"):
                if it.get(key):
                    fp["assets"][it[key]] = sha_file(it[key])
    review_id = hashlib.sha256(json.dumps(fp, sort_keys=True).encode("utf-8")).hexdigest()
    n_err = sum(1 for i in issues if i["severity"] == "error")
    n_warn = len(issues) - n_err
    out = {"review_id": review_id, "passed": n_err == 0, "issues": issues, "as_of_date": run["as_of_date"],
           "checked_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "stats": {"errors": n_err, "warnings": n_warn, **stats}}
    sys.stdout.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    receipt.finish("completed", input_count=len(briefs), output_count=1, cost_usd=0.0, cost_is_estimate=False,
                   passed=out["passed"], errors=n_err, warnings=n_warn, review_id=review_id)
    print(f"check_content: passed={out['passed']} errors={n_err} warnings={n_warn} review_id={review_id[:12]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check_content.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
