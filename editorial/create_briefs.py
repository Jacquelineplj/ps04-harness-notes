#!/usr/bin/env python3
"""Develop exactly three editorial briefs (pieces 01, 02, 03) from accepted evidence.

stdin: decision JSONL. Reads RUN_DIR/eligible.jsonl for the accepted items and
their retained text/segments, calls the model once for all three briefs, then
validates every evidence locator deterministically:
  - text quotes must exist verbatim in the retained text (whitespace-normalised);
    near-misses (curly quotes, dashes, small drift) are replaced by the exact
    retained wording and flagged quote_repaired;
  - segment ids must exist in the transcript;
  - item/version ids must belong to accepted items.
Unresolvable evidence is removed; a claim with no evidence left is dropped and
recorded. Structural failures get one model repair pass. If the briefs still do
not meet the minimums (three distinct pieces, >= 3 independent publishers each,
>= 1 inference claim each) the stage exits 1 and writes briefs.rejected.json.
Nothing is ever invented to fill a gap.

Long transcripts are first condensed by a cheaper model into verbatim excerpts
(segment ids), cached in RUN_DIR/evidence_excerpts.jsonl.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import (find_quote, item_header, load_segments, load_text, normalize_ws,  # noqa: E402
                          render_segments, segment_by_id)
from lib.llm import LLMError, complete, stage_settings  # noqa: E402
from lib.receipt import Receipt  # noqa: E402

STAGE = "create_briefs"
PIECES = ("01", "02", "03")
ITEM_CHARS = int(os.environ.get("BRIEF_ITEM_CHARS", "30000"))
MIN_PUBLISHERS = 3
MIN_CLAIMS = 3
CLAIM_TYPES = ("reported_fact", "source_claim", "inference")

LOCATOR = {"type": "object",
           "properties": {"type": {"type": "string", "enum": ["text", "segment"]},
                          "quote": {"type": ["string", "null"]},
                          "segment_id": {"type": ["string", "null"]}},
           "required": ["type", "quote", "segment_id"], "additionalProperties": False}
EVIDENCE = {"type": "object",
            "properties": {"item_id": {"type": "string"}, "version_id": {"type": "string"}, "locator": LOCATOR},
            "required": ["item_id", "version_id", "locator"], "additionalProperties": False}
CLAIM = {"type": "object",
         "properties": {"claim_id": {"type": "string"}, "statement": {"type": "string"},
                        "type": {"type": "string", "enum": list(CLAIM_TYPES)},
                        "evidence": {"type": "array", "items": EVIDENCE}},
         "required": ["claim_id", "statement", "type", "evidence"], "additionalProperties": False}
BRIEF = {"type": "object",
         "properties": {"piece_id": {"type": "string", "enum": list(PIECES)}, "title": {"type": "string"},
                        "question": {"type": "string"}, "argument": {"type": "string"}, "synthesis": {"type": "string"},
                        "limitations": {"type": "string"}, "claims": {"type": "array", "items": CLAIM}},
         "required": ["piece_id", "title", "question", "argument", "synthesis", "limitations", "claims"],
         "additionalProperties": False}
SCHEMA = {"type": "object", "properties": {"briefs": {"type": "array", "items": BRIEF}},
          "required": ["briefs"], "additionalProperties": False}
EXCERPT_SCHEMA = {"type": "object",
                  "properties": {"excerpts": {"type": "array", "items": {
                      "type": "object",
                      "properties": {"segment_id": {"type": "string"}, "why": {"type": "string"}},
                      "required": ["segment_id", "why"], "additionalProperties": False}}},
                  "required": ["excerpts"], "additionalProperties": False}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def log(msg):
    print(f"create_briefs: {msg}", file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------- evidence pack

def condense_transcript(item: dict, segments: list, run_dir: str, receipt: Receipt, settings: dict, cache: dict) -> str:
    """Ask a cheaper model for the most relevant verbatim segments of a long transcript."""
    key = f"{item['item_id']}@{item['version_id']}"
    if key in cache:
        ids = cache[key]
    else:
        system = ("You condense a long transcript for an editor. Select the 10 to 16 segments most relevant to agent harness "
                  "engineering (how agents are built, evaluated, operated: context management, tools and MCP, sandboxing, "
                  "memory, evals, orchestration, observability) and to concrete claims, numbers, or practitioner experience. "
                  "Return segment ids exactly as shown. Respond with JSON only.")
        user = f"{item_header(item)}\n\nTRANSCRIPT:\n{render_segments(segments)}"
        try:
            res = complete(system=system, user=user, schema=EXCERPT_SCHEMA, stage=STAGE, run_dir=run_dir,
                           label=f"condense:{item['item_id']}", settings=settings)
            receipt.add_model_usage(res["usage"])
            ids = [e["segment_id"] for e in (res["data"] or {}).get("excerpts", []) if segment_by_id(segments, e.get("segment_id"))]
        except LLMError as exc:
            receipt.add_error(f"condense failed for {item['item_id']}: {exc}")
            ids = []
        cache[key] = ids
        with open(os.path.join(run_dir, "evidence_excerpts.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"item_id": item["item_id"], "version_id": item["version_id"], "segment_ids": ids}) + "\n")
    if not ids:
        return render_segments(segments, max_chars=ITEM_CHARS)
    chosen = []
    index = {s["segment_id"]: i for i, s in enumerate(segments)}
    for sid in ids:
        i = index.get(sid)
        if i is None:
            continue
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(segments) and j not in chosen:
                chosen.append(j)
    chosen.sort()
    opening = render_segments(segments, max_chars=1500)
    body = "\n".join(render_segments([segments[j]]) for j in chosen)
    return (f"{opening}\n[... selected excerpts follow; the full transcript has {len(segments)} segments ...]\n{body}")


def evidence_pack(items: list, decisions: dict, run_dir: str, receipt: Receipt, condense_settings: dict) -> str:
    blocks = []
    cache = {}
    for it in items:
        d = decisions[it["item_id"]]
        head = item_header(it)
        head += f"\neditor's decision: accept for pieces {','.join(d.get('piece_ids') or [])}; reason: {d.get('reason')}"
        if d.get("credibility_notes"):
            head += f"\ncredibility notes: {d['credibility_notes']}"
        if it.get("segments_path"):
            segs = load_segments(it)
            full = render_segments(segs)
            body = full if len(full) <= ITEM_CHARS else condense_transcript(it, segs, run_dir, receipt, condense_settings, cache)
            body = "TRANSCRIPT (cite with segment ids):\n" + body
        else:
            text = load_text(it)
            if len(text) > ITEM_CHARS:
                text = text[:ITEM_CHARS] + f"\n[... text truncated; {len(load_text(it)) - ITEM_CHARS} more characters not shown ...]"
            body = "RETAINED TEXT (cite with verbatim quotes):\n" + text
        blocks.append(f"{head}\n\n{body}")
    return "\n\n==========\n\n".join(blocks)


# ----------------------------------------------------------------------------- validation

def best_window(text: str, quote: str):
    """Fuzzy fallback: best matching window of retained text, ratio >= 0.9."""
    nt, nq = normalize_ws(text), normalize_ws(quote)
    if not nq or len(nq) < 15:
        return None
    words = nt.split(" ")
    qlen = len(nq.split(" "))
    best, best_ratio = None, 0.0
    step = max(1, qlen // 4)
    for i in range(0, max(1, len(words) - qlen + 1), step):
        cand = " ".join(words[i:i + qlen])
        r = difflib.SequenceMatcher(None, cand.lower(), nq.lower()).ratio()
        if r > best_ratio:
            best, best_ratio = cand, r
    return best if best_ratio >= 0.9 else None


def validate(briefs: list, items_by_id: dict, publishers: dict) -> tuple:
    """Returns (cleaned briefs, problems list, stats). Mutates nothing passed in."""
    problems, stats = [], {"quotes_exact": 0, "quotes_repaired": 0, "evidence_dropped": 0, "claims_dropped": 0, "version_fixed": 0}
    cleaned = []
    seen_pieces = set()
    for b in briefs:
        pid = b.get("piece_id")
        if pid not in PIECES or pid in seen_pieces:
            problems.append(f"brief piece_id {pid!r} invalid or duplicated")
            continue
        seen_pieces.add(pid)
        nb = {k: b.get(k) for k in ("piece_id", "title", "question", "argument", "synthesis", "limitations")}
        for k, v in nb.items():
            if not isinstance(v, str) or not v.strip():
                problems.append(f"{pid}: field {k} empty")
        claims, ids, dropped = [], set(), []
        for c in b.get("claims") or []:
            cid = str(c.get("claim_id") or "")
            if not re.fullmatch(rf"{pid}-c\d+", cid) or cid in ids:
                cid = f"{pid}-c{len(claims) + len(dropped) + 1}"
            ids.add(cid)
            if c.get("type") not in CLAIM_TYPES:
                problems.append(f"{cid}: bad claim type {c.get('type')!r}")
                continue
            evs = []
            for ev in c.get("evidence") or []:
                item = items_by_id.get(ev.get("item_id"))
                if not item:
                    problems.append(f"{cid}: evidence item {ev.get('item_id')!r} is not an accepted item")
                    stats["evidence_dropped"] += 1
                    continue
                version = item["version_id"]
                if ev.get("version_id") != version:
                    stats["version_fixed"] += 1
                loc = ev.get("locator") or {}
                if loc.get("type") == "text":
                    if item.get("segments_path"):
                        problems.append(f"{cid}: text quote used for media item {item['item_id']}; use a segment id")
                        stats["evidence_dropped"] += 1
                        continue
                    text = load_text(item)
                    hit = find_quote(text, loc.get("quote") or "")
                    if hit["found"] and hit["exact"]:
                        quote = hit["exact"]
                        stats["quotes_exact" if hit["mode"] == "exact" else "quotes_repaired"] += 1
                        repaired = hit["mode"] != "exact"
                    else:
                        win = best_window(text, loc.get("quote") or "")
                        if win:
                            quote, repaired = win, True
                            stats["quotes_repaired"] += 1
                        else:
                            problems.append(f"{cid}: quote not found in {item['item_id']}: {(loc.get('quote') or '')[:80]!r}")
                            stats["evidence_dropped"] += 1
                            continue
                    nev = {"item_id": item["item_id"], "version_id": version, "locator": {"type": "text", "quote": quote}}
                    if repaired:
                        nev["quote_repaired"] = True
                    evs.append(nev)
                elif loc.get("type") == "segment":
                    if not item.get("segments_path"):
                        problems.append(f"{cid}: segment locator used for written item {item['item_id']}")
                        stats["evidence_dropped"] += 1
                        continue
                    seg = segment_by_id(load_segments(item), loc.get("segment_id"))
                    if not seg:
                        problems.append(f"{cid}: segment {loc.get('segment_id')!r} not in {item['item_id']}")
                        stats["evidence_dropped"] += 1
                        continue
                    evs.append({"item_id": item["item_id"], "version_id": version,
                                "locator": {"type": "segment", "segment_id": seg["segment_id"]}})
                else:
                    problems.append(f"{cid}: unknown locator type {loc.get('type')!r}")
                    stats["evidence_dropped"] += 1
            if not evs:
                dropped.append({"claim_id": cid, "statement": c.get("statement"), "reason": "no resolvable evidence"})
                stats["claims_dropped"] += 1
                continue
            claims.append({"claim_id": cid, "statement": (c.get("statement") or "").strip(), "type": c["type"], "evidence": evs})
        nb["claims"] = claims
        nb["dropped_claims"] = dropped
        pubs = {publishers.get(ev["item_id"]) for c in claims for ev in c["evidence"]}
        pubs.discard(None)
        nb["publishers"] = sorted(pubs)
        nb["evidence_items"] = sorted({ev["item_id"] for c in claims for ev in c["evidence"]})
        if len(claims) < MIN_CLAIMS:
            problems.append(f"{pid}: only {len(claims)} valid claims (minimum {MIN_CLAIMS})")
        if len(pubs) < MIN_PUBLISHERS:
            problems.append(f"{pid}: evidence spans {len(pubs)} independent publishers (minimum {MIN_PUBLISHERS})")
        if not any(c["type"] == "inference" and len({ev['item_id'] for ev in c['evidence']}) >= 2 for c in claims):
            problems.append(f"{pid}: no inference claim combining two or more items")
        cleaned.append(nb)
    for pid in PIECES:
        if pid not in seen_pieces:
            problems.append(f"brief {pid} missing")
    cleaned.sort(key=lambda b: b["piece_id"])
    return cleaned, problems, stats


def blocking(problems: list) -> list:
    """Problems that make the brief set unusable (vs. per-evidence drops already handled)."""
    keys = ("missing", "invalid or duplicated", "valid claims", "independent publishers", "no inference claim", "field")
    return [p for p in problems if any(k in p for k in keys)]


# ----------------------------------------------------------------------------- main

def main(run_dir: str) -> int:
    settings = stage_settings(STAGE, run_dir)
    condense_settings = stage_settings("select_items", run_dir)
    receipt = Receipt(run_dir, STAGE, tools=[f"llm:{settings['provider']}"])
    decisions = {}
    n_in = 0
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        n_in += 1
        try:
            d = json.loads(line)
            decisions[d["item_id"]] = d
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            receipt.add_error(f"line {n}: malformed decision ({exc})")
            receipt.finish("invalid_input", input_count=n_in, output_count=0)
            return 2
    eligible = {}
    with open(os.path.join(run_dir, "eligible.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                it = json.loads(line)
                eligible[it["item_id"]] = it
    accepted = []
    for item_id, d in decisions.items():
        if d.get("decision") != "accept":
            continue
        it = eligible.get(item_id)
        if not it:
            receipt.add_error(f"accepted item {item_id} is not in eligible.jsonl; ignored")
            continue
        if it.get("version_id") != d.get("version_id"):
            receipt.add_error(f"accepted item {item_id}: decision version differs from eligible version; using eligible version")
        accepted.append(it)
    publishers = {it["item_id"]: it.get("publisher_id") for it in accepted}
    kinds = {it["kind"] for it in accepted}
    n_pubs = len(set(publishers.values()))
    if len(accepted) < MIN_CLAIMS or n_pubs < MIN_PUBLISHERS:
        msg = f"insufficient evidence: {len(accepted)} accepted items from {n_pubs} publishers (need >= {MIN_CLAIMS} items and >= {MIN_PUBLISHERS} publishers)"
        receipt.add_error(msg, code="insufficient_evidence")
        receipt.finish("failed", input_count=n_in, output_count=0, accepted_items=len(accepted), publishers=n_pubs)
        log(msg)
        return 1
    missing_kinds = sorted(set(("feed", "youtube", "podcast")) - kinds)
    if missing_kinds:
        receipt.add_error(f"accepted evidence lacks kinds {missing_kinds}; the series cannot cover every input type", code="kind_coverage")
    project = read(os.path.join(run_dir, "config", "project.json"))
    policy = read(os.path.join(run_dir, "config", "editorial_policy.md"))
    prompt = read(os.path.join(run_dir, "prompts", "create_briefs.md"))
    system = (f"PROJECT BRIEF (JSON):\n{project}\n\nEDITORIAL POLICY:\n{policy}\n\nINSTRUCTIONS:\n{prompt}\n\n"
              "Respond with JSON matching the provided schema and nothing else.")
    pack = evidence_pack(accepted, decisions, run_dir, receipt, condense_settings)
    user = (f"ACCEPTED EVIDENCE ({len(accepted)} items from {n_pubs} publishers; kinds: {sorted(kinds)}).\n"
            f"Create the three briefs now. Quote written items verbatim; cite transcripts by segment id.\n\n{pack}")
    try:
        res = complete(system=system, user=user, schema=SCHEMA, stage=STAGE, run_dir=run_dir, label="briefs", settings=settings)
    except LLMError as exc:
        receipt.add_error(str(exc))
        receipt.finish("failed", input_count=n_in, output_count=0)
        log(f"model call failed: {exc}")
        return 1
    receipt.add_model_usage(res["usage"])
    briefs = (res["data"] or {}).get("briefs") or []
    cleaned, problems, stats = validate(briefs, {it["item_id"]: it for it in accepted}, publishers)
    log(f"validation pass 1: {stats}; {len(problems)} problems")
    attempts = 1
    if blocking(problems):
        attempts += 1
        repair_user = (f"The briefs below failed validation. Fix ONLY the listed problems: re-copy quotes exactly from the "
                       f"retained text, replace evidence that cannot be located, add missing inference claims or publishers "
                       f"only from the evidence provided, and keep everything else unchanged. Problems:\n- " +
                       "\n- ".join(problems) + f"\n\nCURRENT BRIEFS (JSON):\n{json.dumps(briefs, ensure_ascii=False)}\n\n"
                       f"EVIDENCE:\n{pack}")
        try:
            res2 = complete(system=system, user=repair_user, schema=SCHEMA, stage=STAGE, run_dir=run_dir, label="repair", settings=settings)
            receipt.add_model_usage(res2["usage"])
            briefs2 = (res2["data"] or {}).get("briefs") or []
            cleaned2, problems2, stats2 = validate(briefs2, {it["item_id"]: it for it in accepted}, publishers)
            log(f"validation pass 2: {stats2}; {len(problems2)} problems")
            if len(blocking(problems2)) <= len(blocking(problems)):
                cleaned, problems, stats = cleaned2, problems2, stats2
        except LLMError as exc:
            receipt.add_error(f"repair call failed: {exc}")
    for p in problems:
        receipt.add_error(p, code="validation")
    if blocking(problems):
        with open(os.path.join(run_dir, "briefs.rejected.json"), "w", encoding="utf-8") as fh:
            json.dump({"problems": problems, "briefs": cleaned}, fh, indent=2, ensure_ascii=False)
        receipt.finish("failed", input_count=n_in, output_count=0, validation=stats, attempts=attempts,
                       accepted_items=len(accepted), publishers=n_pubs, missing_kinds=missing_kinds)
        log("briefs did not meet the minimum requirements; see briefs.rejected.json")
        return 1
    for b in cleaned:
        b["model"] = settings["model"]
        b["validation"] = {"quotes_repaired": sum(1 for c in b["claims"] for ev in c["evidence"] if ev.get("quote_repaired")),
                           "dropped_claims": len(b["dropped_claims"])}
        sys.stdout.write(json.dumps(b, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    status = "completed_with_errors" if receipt.errors else "completed"
    receipt.finish(status, input_count=n_in, output_count=len(cleaned), validation=stats, attempts=attempts,
                   accepted_items=len(accepted), publishers=n_pubs, missing_kinds=missing_kinds,
                   evidence_items_used=sorted({i for b in cleaned for i in b["evidence_items"]}))
    log(f"wrote {len(cleaned)} briefs ({stats})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: create_briefs.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
