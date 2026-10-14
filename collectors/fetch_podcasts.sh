#!/usr/bin/env bash
# Collector entry point: configured sources in RUN_DIR/config/sources.json -> candidate JSONL on stdout.
# Exit 0 when every configured source was collected, 1 when any source failed (partial
# results are still emitted), 2 for invalid arguments or configuration.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" collectors/fetch_podcasts.py "$RUN_DIR"
