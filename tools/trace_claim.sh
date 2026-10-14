#!/usr/bin/env bash
# Read-only trace of one published claim back to its evidence.
#   bash tools/trace_claim.sh runs/RUN_ID 01-c2
# Prints: claim -> brief -> editorial decision -> stored evidence version -> exact passage
# (or transcript segment with timestamp) -> audience link.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
CLAIM="${2:-}"; [ -n "$CLAIM" ] || die_invalid "usage: trace_claim.sh RUN_DIR CLAIM_ID"
exec "$PIPELINE_PYTHON" - "$RUN_DIR" "$CLAIM" <<'PY'
import json, os, subprocess, sys
sys.path.insert(0, os.environ["PIPELINE_ROOT"])
from lib.evidence import read_jsonl, resolve_evidence, media_link, fmt_timestamp
run_dir, claim_id = sys.argv[1:]
piece = claim_id.split("-")[0]
briefs = {b["piece_id"]: b for b in read_jsonl(os.path.join(run_dir, "briefs.jsonl"))}
brief = briefs[piece]
claim = next(c for c in brief["claims"] if c["claim_id"] == claim_id)
decisions = {d["item_id"]: d for d in read_jsonl(os.path.join(run_dir, "decisions.jsonl"))}
eligible = {i["item_id"]: i for i in read_jsonl(os.path.join(run_dir, "eligible.jsonl"))}
print(f"CLAIM {claim_id} [{claim['type']}]\n  {claim['statement']}\n")
print(f"BRIEF {piece}: {brief['title']}\n  argument: {brief['argument'][:300]}\n")
for art in ("articles", "video_scripts"):
    p = os.path.join(run_dir, art, f"{piece}.md")
    if os.path.exists(p):
        hits = [l.strip() for l in open(p, encoding="utf-8") if f"[{claim_id}]" in l]
        print(f"USED IN {art}/{piece}.md: {len(hits)} line(s)")
        for h in hits[:2]:
            print(f"  > {h[:220]}")
print()
for ev in claim["evidence"]:
    d = decisions.get(ev["item_id"], {})
    print(f"EVIDENCE item {ev['item_id']} version {ev['version_id'][:12]}...")
    print(f"  editorial decision: {d.get('decision')} (pieces {d.get('piece_ids')}) - {d.get('reason', '')[:240]}")
    rec = subprocess.run(["bash", "data/store.sh", "get", ev["item_id"], ev["version_id"]], capture_output=True, text=True)
    if rec.returncode != 0:
        print(f"  STORE: not found ({rec.stderr.strip()})")
        continue
    item = json.loads(rec.stdout)
    print(f"  stored version: {item['kind']} | {item['publisher_id']} | {item['title']} | published {item['published_at']} | retrieved {item['retrieved_at']}")
    print(f"  retained text: {item['text_path']}" + (f" | segments: {item['segments_path']}" if item.get('segments_path') else ""))
    res = resolve_evidence(ev, item)
    loc = ev["locator"]
    if loc["type"] == "text":
        print(f"  passage ({'found' if res['ok'] else 'NOT FOUND'}): \"{res.get('passage') or loc.get('quote')}\"")
    else:
        print(f"  segment {loc['segment_id']} at {fmt_timestamp(res.get('start_seconds'))}-{fmt_timestamp(res.get('end_seconds'))}: \"{res.get('passage')}\"")
    print(f"  audience link: {media_link(item, res.get('start_seconds'))}\n")
PY
