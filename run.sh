#!/usr/bin/env bash
# Pipeline entry point.
#   bash run.sh [--label TEXT]                       new live run (collect -> series -> checks -> awaiting_review)
#   bash run.sh --replay runs/PREV [--inject FILE]   replay of a previous run's candidate streams (no collection)
#   bash run.sh --package runs/RUN_ID                rerun checks, prepare the package after human approval, refresh summary
#   --until collect|select                           stop after collection or after editorial selection (inspection runs)
# Exit codes: 0 completed, 1 failed/incomplete stage, 2 invalid configuration or arguments.
set -uo pipefail
. "$(dirname "$0")/lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
command -v jq >/dev/null || { log "jq is required"; exit "$EXIT_FAILURE"; }

usage() { sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//' >&2; exit "$EXIT_INVALID"; }
MODE="${RUN_MODE:-live}"; LABEL=""; REPLAY_FROM=""; INJECT=""; PACKAGE_DIR=""; UNTIL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --package) PACKAGE_DIR="${2:-}"; [ -n "$PACKAGE_DIR" ] || usage; shift 2 ;;
    --replay) REPLAY_FROM="${2:-}"; [ -n "$REPLAY_FROM" ] || usage; MODE=replay; shift 2 ;;
    --inject) INJECT="${2:-}"; [ -n "$INJECT" ] || usage; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --until) UNTIL="${2:-}"; case "$UNTIL" in collect|select) ;; *) usage ;; esac; shift 2 ;;
    -h|--help) usage ;;
    *) log "unknown argument: $1"; usage ;;
  esac
done

validate_config() {
  local ok=1
  jq -e 'type=="object" and all(.publication_name, .topic, .audience, .central_question; type=="string" and length>0)' config/project.json >/dev/null 2>&1 \
    || { log "config/project.json must contain nonempty publication_name, topic, audience, central_question"; ok=0; }
  jq -e 'type=="array" and length>0 and all(.[]; (.source_id|type)=="string" and (.publisher_id|type)=="string" and (.url|type)=="string" and (.kind=="feed" or .kind=="youtube" or .kind=="podcast"))' config/sources.json >/dev/null 2>&1 \
    || { log "config/sources.json must be a nonempty array of {source_id, publisher_id, kind(feed|youtube|podcast), url}"; ok=0; }
  for f in config/editorial_policy.md prompts/select_items.md prompts/create_briefs.md prompts/write_articles.md prompts/write_video_scripts.md; do
    [ -s "$f" ] || { log "$f is empty; populate it before a live run"; ok=0; }
  done
  [ "$ok" -eq 1 ] || exit "$EXIT_INVALID"
}

summarize() {  # always last; prints the summary JSON
  local rc="$1"
  if bash reporting/summarize_run.sh "$RUN_DIR" > "$RUN_DIR/summary.json.tmp" 2>>"$RUN_DIR/logs/summarize.stderr.log"; then
    mv "$RUN_DIR/summary.json.tmp" "$RUN_DIR/summary.json"
  else
    rm -f "$RUN_DIR/summary.json.tmp"
    printf '{"run_id": "%s", "status": "failed", "error": "summarize_run failed; see logs/summarize.stderr.log"}\n' "$(jq -r .run_id "$RUN_DIR/run.json")" > "$RUN_DIR/summary.json"
  fi
  cat "$RUN_DIR/summary.json"
  log "run $(jq -r .run_id "$RUN_DIR/run.json") finished with exit $rc, status $(jq -r .status "$RUN_DIR/summary.json")"
}

# ----------------------------------------------------------------------------- package mode
if [ -n "$PACKAGE_DIR" ]; then
  RUN_DIR="$(require_run_dir "$PACKAGE_DIR")" || exit $?
  export RUN_DIR
  STARTED="$(utc_now)"
  log "package mode for $RUN_DIR: rerunning content checks (drafts and snapshots are not modified)"
  [ -f "$RUN_DIR/review.json" ] && cp "$RUN_DIR/review.json" "$RUN_DIR/logs/review-$(date -u +%Y%m%dT%H%M%SZ).json"
  if bash review/check_content.sh "$RUN_DIR" > "$RUN_DIR/review.json.tmp"; then
    mv "$RUN_DIR/review.json.tmp" "$RUN_DIR/review.json"
  else
    rm -f "$RUN_DIR/review.json.tmp"; log "content checks could not run"
    write_receipt "$RUN_DIR" run failed "$STARTED" --error "check_content failed in package mode" >/dev/null
    summarize 1; exit "$EXIT_FAILURE"
  fi
  bash publishing/prepare_package.sh "$RUN_DIR" > "$RUN_DIR/package.manifest.tmp"; rc=$?
  if [ "$rc" -eq 0 ]; then mv "$RUN_DIR/package.manifest.tmp" "$RUN_DIR/package/manifest.json"; else rm -f "$RUN_DIR/package.manifest.tmp"; fi
  write_receipt "$RUN_DIR" run "$( [ "$rc" -eq 0 ] && echo completed || echo failed )" "$STARTED" --extra-json '{"mode":"package"}' >/dev/null
  summarize "$rc"
  exit "$rc"
fi

# ----------------------------------------------------------------------------- new run
validate_config
RUNS_DIR="${RUNS_DIR:-runs}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
[ -n "$LABEL" ] && RUN_ID="$RUN_ID-$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '-')"
RUN_DIR="$RUNS_DIR/$RUN_ID"
while [ -e "$RUN_DIR" ]; do RUN_ID="$RUN_ID-$RANDOM"; RUN_DIR="$RUNS_DIR/$RUN_ID"; done
mkdir -p "$RUN_DIR/logs" "$RUN_DIR/candidates"
export RUN_DIR
STARTED="$(utc_now)"
REPLAY_OF=""
if [ "$MODE" = "replay" ]; then
  REPLAY_OF="$(require_run_dir "$REPLAY_FROM")" || exit $?
fi
"$PIPELINE_PYTHON" - "$RUN_DIR" "$RUN_ID" "$STARTED" "$MODE" "$LABEL" "$REPLAY_OF" "$INJECT" "$RUNS_DIR" "$UNTIL" <<'PY'
import glob, hashlib, json, os, subprocess, sys
run_dir, run_id, started, mode, label, replay_of, inject, runs_dir, until = sys.argv[1:]
def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()
previous = None
if replay_of:
    previous = json.load(open(os.path.join(replay_of, "run.json")))["run_id"]
else:
    runs = sorted(d for d in glob.glob(os.path.join(runs_dir, "*")) if os.path.isfile(os.path.join(d, "run.json")) and os.path.abspath(d) != os.path.abspath(run_dir))
    if runs:
        previous = json.load(open(os.path.join(runs[-1], "run.json")))["run_id"]
def tool_version(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
    except Exception:
        return None
git = tool_version(["git", "rev-parse", "--short", "HEAD"])
run = {"run_id": run_id, "started_at": started, "as_of_date": started[:10], "mode": mode, "previous_run_id": previous,
       "label": label or None, "replay_of": replay_of or None, "inject_file": inject or None, "stop_after": until or None,
       "simulated_failures": os.environ.get("SIMULATE_COLLECTOR_FAILURE") or None,
       "policy_sha256": sha("config/editorial_policy.md"),
       "prompts_sha256": {os.path.basename(p): sha(p) for p in sorted(glob.glob("prompts/*.md"))},
       "sources_sha256": sha("config/sources.json"),
       "tool_versions": {"python": sys.version.split()[0], "yt-dlp": tool_version([sys.executable, "-m", "yt_dlp", "--version"]),
                         "claude_cli": tool_version(["claude", "--version"]), "git_commit": git},
       "llm_provider": os.environ.get("LLM_PROVIDER") or json.load(open("config/models.json")).get("default_provider")}
json.dump(run, open(os.path.join(run_dir, "run.json"), "w"), indent=2)
open(os.path.join(run_dir, "run.json"), "a").write("\n")
PY
cp -R config "$RUN_DIR/config"
cp -R prompts "$RUN_DIR/prompts"
log "run $RUN_ID (mode $MODE, as of $(jq -r .as_of_date "$RUN_DIR/run.json")) started; snapshots saved"
bash data/store.sh init || { log "evidence store init failed"; write_receipt "$RUN_DIR" run failed "$STARTED" --error "store init failed" >/dev/null; summarize 1; exit "$EXIT_FAILURE"; }

FINAL=0
bash workflows/collect_sources.sh "$RUN_DIR"; rc_collect=$?
[ "$rc_collect" -gt "$FINAL" ] && FINAL=$rc_collect
if [ "$rc_collect" -eq 2 ]; then
  log "collection reported invalid configuration or input; series not attempted"
elif [ "$UNTIL" = "collect" ]; then
  log "stopping after collection as requested (--until collect)"
elif [ -s "$RUN_DIR/eligible.jsonl" ]; then
  [ "$rc_collect" -ne 0 ] && log "collection incomplete (exit $rc_collect); continuing with usable evidence"
  STOP_AFTER="$UNTIL" bash workflows/create_series.sh "$RUN_DIR"; rc_series=$?
  [ "$rc_series" -gt "$FINAL" ] && FINAL=$rc_series
else
  log "no eligible evidence after collection; series not attempted"
  [ "$FINAL" -eq 0 ] && FINAL=1
fi
write_receipt "$RUN_DIR" run "$( [ "$FINAL" -eq 0 ] && echo completed || echo completed_with_errors )" "$STARTED" \
  --extra-json "{\"mode\":\"$MODE\",\"exit_code\":$FINAL,\"collect_exit\":$rc_collect,\"series_exit\":${rc_series:-null}}" >/dev/null
summarize "$FINAL"
exit "$FINAL"
