#!/usr/bin/env bash
# Commands for demo/technical_demo_script_v2.md, in recording order. All read-only.
# While recording: paste one block, wait for the output, then read that step's narration.
# Before recording: run this file to warm every command up.

cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null || true

# Step 0 — no command: open SUBMISSION.md at the architecture diagram.

# Step 1 — entry point and components
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
sed -n '3,5p' run.sh

# Step 2.1 — trace one claim back to its source
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9

# Step 2.2 — no command: open the published third article, search 16,000 then 30:48.

# Step 3.1 — the two repeat runs
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json

# Step 3.2 — two retained versions of one item
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"

# Step 3.3 — what actually changed
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s

# Step 4 — the run that failed
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json

# Step 5 — the correction and the policy revision
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md

# Step 6.1 — the storage tradeoff
ls -l data/assets/feed/d32c876482ebf166/

# Step 6.2 — where the system stops
ls runs/20261013T213636Z-podcasts-expanded/package

# Optional — simulated collector failure (after step 4)
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json

# Optional — one stage receipt (after step 1)
jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json

# Optional — date-window exclusions (after step 1)
head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'

