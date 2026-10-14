#!/usr/bin/env bash
# Deterministic component checks from examples/README.md, run against a
# disposable evidence directory so fictional fixtures never touch live evidence.
set -uo pipefail
. "$(dirname "$0")/../lib/common.sh"
cd "$PIPELINE_ROOT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/ps04-examples.XXXXXX")"
export EVIDENCE_DIR="$TMP/evidence"
RUN="$TMP/run"
mkdir -p "$RUN/logs"
cp examples/run.json "$RUN/run.json"
fail=0
check() { if [ "$1" -eq 0 ]; then echo "PASS  $2"; else echo "FAIL  $2"; fail=1; fi; }

# 1. initial ingestion -> three new items, in order
bash data/store.sh init
bash data/store.sh upsert "$RUN" < examples/items.jsonl > "$TMP/changes1.jsonl"
"$PIPELINE_PYTHON" - "$TMP/changes1.jsonl" examples/initial_changes_expected.jsonl <<'PY'
import json, sys
got = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
exp = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
sys.exit(0 if got == exp else 1)
PY
check $? "check 1: initial ingestion emits three new items"

# 2. replay -> four unchanged (incl. duplicate + refreshed retrieval) then one changed
bash data/store.sh upsert "$RUN" < examples/replay_items.jsonl > "$TMP/changes2.jsonl"
"$PIPELINE_PYTHON" - "$TMP/changes2.jsonl" examples/replay_changes_expected.jsonl <<'PY'
import json, sys
got = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
exp = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
sys.exit(0 if got == exp else 1)
PY
check $? "check 2: replay emits 4 unchanged + 1 changed"
n_items=$(bash data/store.sh list | wc -l | tr -d ' ')
[ "$n_items" = "3" ]; check $? "check 2b: store still holds three logical items (got $n_items)"
bash data/store.sh get podcast:fictional-episode 8f4fc03210022af1be3798fa7355ae3fa40297873b3ed037420ded36c5849bd5 >/dev/null 2>&1
check $? "check 2c: first podcast version remains retrievable"
latest=$(bash data/store.sh get podcast:fictional-episode | "$PIPELINE_PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["version_id"])')
[ "$latest" = "ed221b9c9d6af72c61b3881e7ef697bf8c4a36bfe6fcffb8e6542953118979c5" ]; check $? "check 2d: latest podcast version is the changed one"
bash data/store.sh get no:such-item >/dev/null 2>&1; [ $? -eq 1 ]; check $? "check 2e: get on a missing item exits 1"

# 3. date filter
bash processing/filter_items.sh "$RUN" < examples/filter_input.jsonl > "$TMP/eligible.jsonl"
"$PIPELINE_PYTHON" - "$TMP/eligible.jsonl" "$RUN/exclusions.jsonl" examples/filter_expected.json <<'PY'
import json, sys
elig = {json.loads(l)["item_id"] for l in open(sys.argv[1]) if l.strip()}
excl = {(json.loads(l)["item_id"], json.loads(l)["reason"]) for l in open(sys.argv[2]) if l.strip()}
exp = json.load(open(sys.argv[3]))
ok = elig == set(exp["eligible_item_ids"]) and excl == {(e["item_id"], e["reason"]) for e in exp["exclusions"]}
if not ok:
    print("eligible:", sorted(elig), "\nexclusions:", sorted(excl))
sys.exit(0 if ok else 1)
PY
check $? "check 3: 30-date window and exclusion reasons match filter_expected.json"

# 4. brief references resolve to retained files
"$PIPELINE_PYTHON" - <<'PY'
import json, sys
sys.path.insert(0, ".")
from lib.evidence import resolve_evidence
items = {}
for l in open("examples/items.jsonl"):
    if l.strip():
        r = json.loads(l); items[(r["item_id"], r["version_id"])] = r
bad = 0
for l in open("examples/briefs.jsonl"):
    if not l.strip():
        continue
    brief = json.loads(l)
    for c in brief["claims"]:
        for ev in c["evidence"]:
            item = items.get((ev["item_id"], ev["version_id"]))
            res = resolve_evidence(ev, item) if item else {"ok": False, "problem": "unknown item version"}
            if not res["ok"]:
                bad += 1; print("unresolved:", c["claim_id"], ev, res["problem"])
sys.exit(1 if bad else 0)
PY
check $? "check 4: every brief evidence reference resolves to its retained passage"

rm -rf "$TMP"
[ $fail -eq 0 ] && echo "ALL EXAMPLE CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
