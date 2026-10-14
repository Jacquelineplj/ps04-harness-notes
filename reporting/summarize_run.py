#!/usr/bin/env python3
"""Summarise a run from its artifacts and receipts (no model calls).

Counts are null when the producing stage did not run, 0 for a measured empty
result. Costs are split into known, estimated and unknown; a cost is never
reported as zero merely because a receipt is absent. Status is one of failed,
awaiting_review, ready_for_production.
"""
from __future__ import annotations

import datetime as _dt
import glob
import json
import os
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import read_jsonl  # noqa: E402

STAGES = ["fetch_feeds", "fetch_youtube", "fetch_podcasts", "collect_sources", "extract_content", "store_upsert", "store_list",
          "filter_items", "select_items", "create_briefs", "write_articles", "write_video_scripts", "check_content",
          "create_series", "prepare_package", "run"]
KINDS = ("feed", "youtube", "podcast")


def jsonl_or_none(path):
    if not os.path.exists(path):
        return None
    try:
        return read_jsonl(path)
    except (json.JSONDecodeError, OSError):
        return None


def json_or_none(path):
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def parse_ts(s):
    try:
        return _dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
    except (TypeError, ValueError):
        return None


def coverage(items):
    if items is None:
        return None
    by_kind = {k: 0 for k in KINDS}
    pubs = {}
    for it in items:
        by_kind[it.get("kind")] = by_kind.get(it.get("kind"), 0) + 1
        pubs.setdefault(it.get("publisher_id"), set()).add(it.get("item_id"))
    return {"items": len(items), "by_kind": by_kind, "independent_publishers": len(pubs),
            "publishers": {p: len(v) for p, v in sorted(pubs.items())},
            "meets_minimums": len(items) >= 12 and len(pubs) >= 6 and all(by_kind.get(k, 0) >= 2 for k in KINDS)}


def main(run_dir: str) -> int:
    run = json_or_none(os.path.join(run_dir, "run.json")) or {}
    receipts = []
    for p in sorted(glob.glob(os.path.join(run_dir, "logs", "*.json"))):
        r = json_or_none(p)
        if r and r.get("stage"):
            r["_path"] = p
            receipts.append(r)
    latest = {}
    for r in receipts:
        latest[r["stage"]] = r  # sorted by filename timestamp: last wins

    cand = jsonl_or_none(os.path.join(run_dir, "candidates.jsonl"))
    stream_names = {"feed": "feeds", "youtube": "youtube", "podcast": "podcasts"}
    cand_by_kind = {}
    for k in KINDS:
        p = os.path.join(run_dir, "candidates", f"{stream_names[k]}.jsonl")
        cand_by_kind[k] = len(jsonl_or_none(p) or []) if os.path.exists(p) else None
    items = jsonl_or_none(os.path.join(run_dir, "items.jsonl"))
    changes = jsonl_or_none(os.path.join(run_dir, "changes.jsonl"))
    corpus = jsonl_or_none(os.path.join(run_dir, "corpus.jsonl"))
    eligible = jsonl_or_none(os.path.join(run_dir, "eligible.jsonl"))
    exclusions = jsonl_or_none(os.path.join(run_dir, "exclusions.jsonl"))
    decisions = jsonl_or_none(os.path.join(run_dir, "decisions.jsonl"))
    briefs = jsonl_or_none(os.path.join(run_dir, "briefs.jsonl"))
    articles = jsonl_or_none(os.path.join(run_dir, "articles.jsonl"))
    scripts = jsonl_or_none(os.path.join(run_dir, "video_scripts.jsonl"))
    duplicates = jsonl_or_none(os.path.join(run_dir, "duplicates.jsonl"))
    review = json_or_none(os.path.join(run_dir, "review.json"))
    approval = json_or_none(os.path.join(run_dir, "approval.json"))
    collection = json_or_none(os.path.join(run_dir, "collection_status.json"))
    manifest = json_or_none(os.path.join(run_dir, "package", "manifest.json"))
    links = json_or_none(os.path.join(run_dir, "package", "publication_links.json"))

    def count_changes(kind):
        return None if changes is None else sum(1 for c in changes if c.get("change") == kind)

    def count_dec(kind):
        return None if decisions is None else sum(1 for d in decisions if d.get("decision") == kind)

    def files_present(sub):
        return sum(1 for p in ("01", "02", "03") if os.path.exists(os.path.join(run_dir, sub, f"{p}.md")))

    counts = {
        "discovered": None if cand is None else len(cand),
        "discovered_by_kind": cand_by_kind,
        "duplicate_observations": None if duplicates is None else len(duplicates),
        "extracted": None if items is None else len(items),
        "new": count_changes("new"), "changed": count_changes("changed"), "unchanged": count_changes("unchanged"),
        "corpus": None if corpus is None else len(corpus),
        "eligible": None if eligible is None else len(eligible),
        "excluded": None if exclusions is None else len(exclusions),
        "excluded_by_reason": None if exclusions is None else {r: sum(1 for e in exclusions if e.get("reason") == r) for r in ("outside_window", "unknown_date", "future_date", "invalid_date")},
        "accepted": count_dec("accept"), "rejected": count_dec("reject"), "deferred": count_dec("defer"),
        "briefs": None if briefs is None else len(briefs),
        "articles": None if articles is None else files_present("articles"),
        "video_scripts": None if scripts is None else files_present("video_scripts"),
    }

    # cited evidence coverage (distinct underlying items)
    cited = None
    if briefs is not None and eligible is not None:
        by_id = {it["item_id"]: it for it in eligible}
        used = {ev["item_id"] for b in briefs for c in b.get("claims", []) for ev in c.get("evidence", [])}
        cited = coverage([by_id[i] for i in used if i in by_id])
        cited["meets_minimums"] = None  # minimums apply to collected evidence, not to citations

    # stages
    stages = {}
    for name in STAGES:
        r = latest.get(name)
        if r:
            stages[name] = {"status": r.get("status"), "finished_at": r.get("finished_at"), "elapsed_seconds": r.get("elapsed_seconds"),
                            "input_count": r.get("input_count"), "output_count": r.get("output_count"),
                            "errors": len(r.get("errors") or []), "cost_usd": r.get("cost_usd"),
                            "cost_is_estimate": r.get("cost_is_estimate"), "receipts": sum(1 for x in receipts if x["stage"] == name)}
        else:
            stages[name] = {"status": "not_run", "receipts": 0}
    failed = []
    for name, s in stages.items():
        if s["status"] in ("failed", "invalid_input"):
            failed.append({"stage": name, "status": s["status"]})
        elif s["status"] == "completed_with_errors":
            failed.append({"stage": name, "status": "completed_with_errors", "errors": s["errors"]})
    if collection:
        for k, c in (collection.get("collectors") or {}).items():
            if c.get("exit_code") not in (0, None):
                failed.append({"stage": f"collector:{k}", "status": "exit " + str(c.get("exit_code")), "simulated": c.get("simulated", False)})
    simulated = [{"stage": r["stage"], "message": e.get("message")} for r in receipts for e in (r.get("errors") or []) if e.get("simulated")]

    # models, tools, costs
    models = {}
    tools = set()
    known = estimated = 0.0
    unknown = []
    for r in receipts:
        for t in r.get("tools") or []:
            tools.add(t)
        for m in r.get("models") or []:
            key = f"{m.get('provider')}:{m.get('model')}"
            agg = models.setdefault(key, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "cost_is_estimate": False})
            agg["calls"] += m.get("calls", 0)
            agg["input_tokens"] += m.get("input_tokens", 0)
            agg["output_tokens"] += m.get("output_tokens", 0)
            if m.get("cost_usd") is not None:
                agg["cost_usd"] = round(agg["cost_usd"] + float(m["cost_usd"]), 4)
            agg["cost_is_estimate"] = agg["cost_is_estimate"] or bool(m.get("cost_is_estimate"))
        c = r.get("cost_usd")
        if c is None:
            unknown.append(r["stage"])
        elif r.get("cost_is_estimate"):
            estimated += float(c)
        else:
            known += float(c)
    costs = {"known_usd": round(known, 4), "estimated_usd": round(estimated, 4), "total_including_estimates_usd": round(known + estimated, 4),
             "unknown_cost_stages": sorted(set(unknown)),
             "basis": "Model costs come from the Claude Code CLI's list-price estimate (subscription use is not billed per token); local compute is reported as 0."}

    # elapsed
    started = parse_ts(run.get("started_at"))
    ends = [parse_ts(r.get("finished_at")) for r in receipts]
    ends = [e for e in ends if e]
    elapsed = round((max(ends) - started).total_seconds(), 1) if started and ends else None

    # status
    drafts_ok = counts["articles"] == 3 and counts["video_scripts"] == 3
    review_ok = bool(review and review.get("passed"))
    approval_ok = bool(approval and approval.get("decision") == "approve" and review and approval.get("review_id") == review.get("review_id"))
    if manifest and approval_ok and review_ok and manifest.get("review_id") == review.get("review_id"):
        status = "ready_for_production"
    elif drafts_ok and review_ok:
        status = "awaiting_review"
    else:
        status = "failed"
    remaining = []
    if status == "failed":
        if not drafts_ok:
            remaining.append("repair the failed stage(s) and rerun the series (drafts are incomplete)")
        if review and not review.get("passed"):
            remaining.append("fix the errors listed in review.json and rerun review/check_content.sh")
    if status == "awaiting_review":
        remaining.append("human editorial review of articles, scripts and decisions; record approval.json with the current review_id")
        remaining.append("bash run.sh --package RUN_DIR after approval")
    if status == "ready_for_production":
        remaining.extend(manifest.get("manual_steps") or [])
    published = None
    if links:
        published = {l.get("piece_id"): {"substack_url": l.get("substack_url"), "youtube_url": l.get("youtube_url")} for l in links}
        if not any(v["substack_url"] or v["youtube_url"] for v in published.values()):
            remaining.append("publication links not yet entered in package/publication_links.json")

    summary = {
        "run_id": run.get("run_id"), "mode": run.get("mode"), "label": run.get("label"), "as_of_date": run.get("as_of_date"), "stop_after": run.get("stop_after"),
        "previous_run_id": run.get("previous_run_id"), "replay_of": run.get("replay_of"),
        "status": status, "started_at": run.get("started_at"), "elapsed_seconds": elapsed,
        "summarized_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": counts,
        "coverage": {"collected_eligible": coverage(eligible), "cited_in_briefs": cited,
                     "collection": collection, "coverage_complete": bool(collection) and all((c.get("exit_code") == 0) for c in (collection.get("collectors") or {}).values()) if collection else None},
        "failed_or_incomplete_stages": failed,
        "simulated_failures": simulated,
        "stages": stages,
        "models": models, "tools": sorted(tools), "costs": costs,
        "review": None if not review else {"review_id": review.get("review_id"), "passed": review.get("passed"),
                                            "errors": review.get("stats", {}).get("errors"), "warnings": review.get("stats", {}).get("warnings")},
        "human_decision": None if not approval else {"decision": approval.get("decision"), "reviewer": approval.get("reviewer"),
                                                     "reviewed_at": approval.get("reviewed_at"), "matches_current_review": approval_ok},
        "package": None if not manifest else {"packaged_at": manifest.get("packaged_at"), "pieces": [p["piece_id"] for p in manifest.get("pieces", [])]},
        "published_links": published,
        "remaining_manual_actions": remaining,
        "notes": [n for n in [
            "counts are null for stages that did not run and 0 for measured empty results",
            "duplicate_observations counts podcast/YouTube copies of one recording that were reconciled before counting evidence" if counts["duplicate_observations"] else None,
            "collection was incomplete; coverage limitations are listed under failed_or_incomplete_stages" if any(f["stage"].startswith("collector:") for f in failed) else None,
            f"inspection run stopped after the {run.get('stop_after')} stage by request; no publication was attempted" if run.get("stop_after") else None,
        ] if n],
    }
    sys.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: summarize_run.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
