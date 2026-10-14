#!/usr/bin/env bash
# Collection workflow: three collectors (concurrently) -> candidates.jsonl -> extraction
# -> evidence store upsert -> store list (corpus) -> freshness filter.
# Collector failures are preserved (collection_status.json + receipts); usable results
# continue downstream. Exit 0 complete, 1 incomplete collection or failed step, 2 invalid.
set -uo pipefail
. "$(dirname "$0")/../lib/common.sh"
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
export RUN_DIR
STARTED="$(utc_now)"
mkdir -p "$RUN_DIR/candidates" "$RUN_DIR/logs"
MODE="$(jq -r '.mode // "live"' "$RUN_DIR/run.json")"
REPLAY_OF="$(jq -r '.replay_of // empty' "$RUN_DIR/run.json")"
INJECT="$(jq -r '.inject_file // empty' "$RUN_DIR/run.json")"
SIM="${SIMULATE_COLLECTOR_FAILURE:-}"

rc_feeds=0; rc_youtube=0; rc_podcasts=0
if [ "$MODE" = "replay" ] && [ -n "$REPLAY_OF" ]; then
  log "replay mode: reusing candidate streams from $REPLAY_OF (collectors not run)"
  for k in feeds youtube podcasts; do
    if [ -f "$REPLAY_OF/candidates/$k.jsonl" ]; then cp "$REPLAY_OF/candidates/$k.jsonl" "$RUN_DIR/candidates/$k.jsonl"; else : > "$RUN_DIR/candidates/$k.jsonl"; fi
  done
  if [ -n "$INJECT" ]; then
    [ -f "$INJECT" ] || { log "inject file not found: $INJECT"; exit "$EXIT_INVALID"; }
    cp "$INJECT" "$RUN_DIR/candidates/injected.jsonl"
    log "injected $(grep -c . "$RUN_DIR/candidates/injected.jsonl") previously withheld candidate(s)"
  fi
  write_receipt "$RUN_DIR" fetch_feeds skipped "$STARTED" --extra-json "{\"replayed_from\":\"$REPLAY_OF\"}" >/dev/null
  write_receipt "$RUN_DIR" fetch_youtube skipped "$STARTED" --extra-json "{\"replayed_from\":\"$REPLAY_OF\"}" >/dev/null
  write_receipt "$RUN_DIR" fetch_podcasts skipped "$STARTED" --extra-json "{\"replayed_from\":\"$REPLAY_OF\"}" >/dev/null
else
  log "running collectors concurrently"
  bash collectors/fetch_feeds.sh "$RUN_DIR" > "$RUN_DIR/candidates/feeds.jsonl" 2> "$RUN_DIR/logs/fetch_feeds.stderr.log" & p1=$!
  bash collectors/fetch_youtube.sh "$RUN_DIR" > "$RUN_DIR/candidates/youtube.jsonl" 2> "$RUN_DIR/logs/fetch_youtube.stderr.log" & p2=$!
  bash collectors/fetch_podcasts.sh "$RUN_DIR" > "$RUN_DIR/candidates/podcasts.jsonl" 2> "$RUN_DIR/logs/fetch_podcasts.stderr.log" & p3=$!
  wait "$p1" || rc_feeds=$?
  wait "$p2" || rc_youtube=$?
  wait "$p3" || rc_podcasts=$?
  log "collectors finished: feeds=$rc_feeds youtube=$rc_youtube podcasts=$rc_podcasts"
fi

# Merge records that carry every required candidate field (invalid lines are counted, not hidden).
VALID='fromjson? | select(type=="object" and (.item_id|type)=="string" and (.source_id|type)=="string" and (.publisher_id|type)=="string" and (.kind=="feed" or .kind=="youtube" or .kind=="podcast") and (.title|type)=="string" and (.url|type)=="string" and has("published_at") and (.retrieved_at|type)=="string" and has("media_url"))'
total=0
for f in feeds youtube podcasts injected; do
  [ -f "$RUN_DIR/candidates/$f.jsonl" ] && total=$((total + $(grep -c . "$RUN_DIR/candidates/$f.jsonl" || true)))
done
cat "$RUN_DIR"/candidates/*.jsonl | jq -c -R "$VALID" > "$RUN_DIR/candidates.jsonl"
merged=$(grep -c . "$RUN_DIR/candidates.jsonl" || true)
invalid=$((total - merged))
log "merged $merged valid candidates ($invalid invalid lines dropped)"

sim_json="null"; [ -n "$SIM" ] && sim_json="\"$SIM\""
"$PIPELINE_PYTHON" - "$RUN_DIR" "$MODE" "$REPLAY_OF" "$rc_feeds" "$rc_youtube" "$rc_podcasts" "$merged" "$invalid" "$sim_json" <<'PY'
import json, os, sys
run_dir, mode, replay_of, f, y, p, merged, invalid, sim = sys.argv[1:]
def n(k):
    path = os.path.join(run_dir, "candidates", f"{k}.jsonl")
    return sum(1 for l in open(path) if l.strip()) if os.path.exists(path) else None
status = {"mode": mode, "replay_of": replay_of or None, "simulated_failure": json.loads(sim),
          "collectors": {k: {"exit_code": None if mode == "replay" else int(v), "candidates": n(k),
                             "status": ("replayed" if mode == "replay" else ("ok" if int(v) == 0 else "failed")),
                             "simulated": bool(json.loads(sim)) and json.loads(sim).split(":")[0] == k}
                         for k, v in (("feeds", f), ("youtube", y), ("podcasts", p))},
          "injected": n("injected"), "merged_candidates": int(merged), "invalid_lines": int(invalid)}
json.dump(status, open(os.path.join(run_dir, "collection_status.json"), "w"), indent=2)
PY

# Real pipe: extraction -> items.jsonl -> evidence store, change records captured in order.
bash processing/extract_content.sh "$RUN_DIR" < "$RUN_DIR/candidates.jsonl" \
  | tee "$RUN_DIR/items.jsonl" \
  | bash data/store.sh upsert "$RUN_DIR" > "$RUN_DIR/changes.jsonl"
pipe_status=("${PIPESTATUS[@]}")   # capture all at once: any later command resets PIPESTATUS (bash 3.2)
rc_extract=${pipe_status[0]}; rc_upsert=${pipe_status[2]}
log "extract=$rc_extract upsert=$rc_upsert ($(grep -c . "$RUN_DIR/items.jsonl" || true) items, $(grep -c . "$RUN_DIR/changes.jsonl" || true) change records)"

bash data/store.sh list > "$RUN_DIR/corpus.jsonl"; rc_list=$?
bash processing/filter_items.sh "$RUN_DIR" < "$RUN_DIR/corpus.jsonl" > "$RUN_DIR/eligible.jsonl"; rc_filter=$?
log "list=$rc_list filter=$rc_filter ($(grep -c . "$RUN_DIR/eligible.jsonl" || true) eligible)"

rc=0
for code in "$rc_feeds" "$rc_youtube" "$rc_podcasts" "$rc_extract" "$rc_upsert" "$rc_list" "$rc_filter"; do
  [ "$code" -gt "$rc" ] && rc="$code"
done
errors=""
[ "$rc_feeds" -ne 0 ] && errors="$errors --error feeds_collector_exit_$rc_feeds"
[ "$rc_youtube" -ne 0 ] && errors="$errors --error youtube_collector_exit_$rc_youtube"
[ "$rc_podcasts" -ne 0 ] && errors="$errors --error podcasts_collector_exit_$rc_podcasts"
[ "$rc_extract" -ne 0 ] && errors="$errors --error extract_content_exit_$rc_extract"
[ "$rc_upsert" -ne 0 ] && errors="$errors --error store_upsert_exit_$rc_upsert"
[ "$rc_filter" -ne 0 ] && errors="$errors --error filter_items_exit_$rc_filter"
status=completed
if [ "$rc_extract" -ne 0 ] || [ "$rc_upsert" -ne 0 ] || [ "$rc_list" -ne 0 ] || [ "$rc_filter" -ne 0 ]; then status=failed
elif [ "$rc" -ne 0 ]; then status=completed_with_errors; fi
# shellcheck disable=SC2086
write_receipt "$RUN_DIR" collect_sources "$status" "$STARTED" --input-count "$total" --output-count "$(grep -c . "$RUN_DIR/eligible.jsonl" || true)" \
  --tools "jq,bash" $errors --extra-json "{\"exit_codes\":{\"feeds\":$rc_feeds,\"youtube\":$rc_youtube,\"podcasts\":$rc_podcasts,\"extract\":$rc_extract,\"upsert\":$rc_upsert,\"list\":$rc_list,\"filter\":$rc_filter},\"merged_candidates\":$merged,\"invalid_lines\":$invalid,\"mode\":\"$MODE\"}" >/dev/null
[ "$rc" -ne 0 ] && log "collection incomplete or failed (exit $rc); see collection_status.json and receipts"
exit "$rc"
