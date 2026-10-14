#!/usr/bin/env bash
# Run summary from saved artifacts and receipts. Works for incomplete runs. JSON on stdout.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" reporting/summarize_run.py "$RUN_DIR"
