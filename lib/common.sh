#!/usr/bin/env bash
# Shared helpers for pipeline entry points. Compatible with macOS /bin/bash 3.2.
# Source this file; do not execute it.

PIPELINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PIPELINE_ROOT

if [ -x "$PIPELINE_ROOT/.venv/bin/python" ]; then
  PIPELINE_PYTHON="$PIPELINE_ROOT/.venv/bin/python"
else
  PIPELINE_PYTHON="$(command -v python3 || true)"
fi
export PIPELINE_PYTHON
export PYTHONPATH="$PIPELINE_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

EXIT_OK=0
EXIT_FAILURE=1
EXIT_INVALID=2

utc_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

log() { printf '[%s] %s\n' "$(basename "$0")" "$*" >&2; }

die_invalid() { log "invalid: $*"; exit "$EXIT_INVALID"; }

# Normalise a RUN_DIR argument and verify it holds run.json. Run directories
# normally live under runs/ (printed repository-relative); any other location
# (for example a disposable test directory) is printed as an absolute path.
# Usage: RUN_DIR="$(require_run_dir "$1")" || exit $?
require_run_dir() {
  local arg="$1" abs
  [ -n "$arg" ] || { log "usage: $(basename "$0") RUN_DIR"; return "$EXIT_INVALID"; }
  case "$arg" in
    /*) abs="$arg" ;;
    *) abs="$PIPELINE_ROOT/$arg" ;;
  esac
  abs="$(cd "$abs" 2>/dev/null && pwd)" || { log "run directory not found: $arg"; return "$EXIT_INVALID"; }
  [ -f "$abs/run.json" ] || { log "run.json missing in $arg"; return "$EXIT_INVALID"; }
  case "$abs" in
    "$PIPELINE_ROOT"/*) printf '%s\n' "${abs#"$PIPELINE_ROOT"/}" ;;
    *) printf '%s\n' "$abs" ;;
  esac
}

# Write a receipt from shell. Usage:
#   write_receipt RUN_DIR STAGE STATUS STARTED_AT [--input-count N] [--output-count N]
#                 [--tools a,b] [--error "msg"]... [--extra-json '{...}'] [--cost-usd X]
write_receipt() {
  "$PIPELINE_PYTHON" "$PIPELINE_ROOT/lib/receipt.py" "$@"
}

require_python() {
  [ -n "$PIPELINE_PYTHON" ] && [ -x "$PIPELINE_PYTHON" ] || { log "python3 not found"; exit "$EXIT_FAILURE"; }
}
