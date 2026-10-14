#!/usr/bin/env bash
# Series workflow: selection -> briefs -> articles + video scripts -> content checks.
# Each artifact is saved before the next step. If briefs cannot be supported by the
# eligible evidence the workflow stops and reports the failed requirement (exit 1).
set -uo pipefail
. "$(dirname "$0")/../lib/common.sh"
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
export RUN_DIR
STARTED="$(utc_now)"
finish() {  # finish STATUS RC [errors...]
  local status="$1" rc="$2"; shift 2
  write_receipt "$RUN_DIR" create_series "$status" "$STARTED" --tools bash "$@" >/dev/null
  exit "$rc"
}
[ -s "$RUN_DIR/eligible.jsonl" ] || finish failed 1 --error "no eligible evidence (eligible.jsonl empty or missing)"

bash editorial/select_items.sh "$RUN_DIR" < "$RUN_DIR/eligible.jsonl" > "$RUN_DIR/decisions.jsonl"; rc_select=$?
log "select_items exit $rc_select ($(grep -c . "$RUN_DIR/decisions.jsonl" || true) decisions)"
[ "$rc_select" -eq 2 ] && finish invalid_input 2 --error "select_items_exit_2"
[ -s "$RUN_DIR/decisions.jsonl" ] || finish failed 1 --error "select_items produced no decisions"
if [ "${STOP_AFTER:-}" = "select" ]; then
  log "stopping after editorial selection as requested (STOP_AFTER=select); no briefs or drafts generated"
  finish completed "$rc_select" --extra-json '{"stopped_after":"select"}'
fi

bash editorial/create_briefs.sh "$RUN_DIR" < "$RUN_DIR/decisions.jsonl" > "$RUN_DIR/briefs.jsonl.tmp"; rc_briefs=$?
if [ "$rc_briefs" -ne 0 ] || [ ! -s "$RUN_DIR/briefs.jsonl.tmp" ]; then
  rm -f "$RUN_DIR/briefs.jsonl.tmp"
  log "REQUIREMENT FAILED: briefs could not be supported by the accepted evidence (exit $rc_briefs). Repair the evidence or policy and rerun."
  finish failed "$( [ "$rc_briefs" -eq 2 ] && echo 2 || echo 1 )" --error "create_briefs_exit_$rc_briefs"
fi
mv "$RUN_DIR/briefs.jsonl.tmp" "$RUN_DIR/briefs.jsonl"

bash content/write_articles.sh "$RUN_DIR" < "$RUN_DIR/briefs.jsonl" > "$RUN_DIR/articles.jsonl"; rc_art=$?
bash content/write_video_scripts.sh "$RUN_DIR" < "$RUN_DIR/briefs.jsonl" > "$RUN_DIR/video_scripts.jsonl"; rc_scr=$?
log "write_articles exit $rc_art, write_video_scripts exit $rc_scr"

bash review/check_content.sh "$RUN_DIR" > "$RUN_DIR/review.json.tmp"; rc_check=$?
if [ "$rc_check" -eq 0 ] && [ -s "$RUN_DIR/review.json.tmp" ]; then
  mv "$RUN_DIR/review.json.tmp" "$RUN_DIR/review.json"
else
  rm -f "$RUN_DIR/review.json.tmp"
  finish failed 1 --error "check_content could not run (exit $rc_check)"
fi
passed="$(jq -r '.passed' "$RUN_DIR/review.json")"
errs=""
[ "$rc_select" -ne 0 ] && errs="$errs --error select_items_exit_$rc_select"
[ "$rc_art" -ne 0 ] && errs="$errs --error write_articles_exit_$rc_art"
[ "$rc_scr" -ne 0 ] && errs="$errs --error write_video_scripts_exit_$rc_scr"
if [ "$rc_art" -ne 0 ] || [ "$rc_scr" -ne 0 ]; then
  # shellcheck disable=SC2086
  finish failed 1 $errs
fi
if [ "$passed" != "true" ]; then
  log "content checks reported blocking errors; drafts need repair before review (see review.json)"
  # shellcheck disable=SC2086
  finish completed_with_errors 1 $errs --error "content checks failed (review.json passed=false)"
fi
# shellcheck disable=SC2086
finish "$( [ -z "$errs" ] && echo completed || echo completed_with_errors )" "$( [ -z "$errs" ] && echo 0 || echo 1 )" $errs
