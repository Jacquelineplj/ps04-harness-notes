#!/usr/bin/env bash
# Editorial component entry point (select_items). Reads JSONL on stdin, writes JSONL on stdout.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" editorial/select_items.py "$RUN_DIR"
