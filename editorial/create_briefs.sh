#!/usr/bin/env bash
# Editorial component entry point (create_briefs). Reads JSONL on stdin, writes JSONL on stdout.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" editorial/create_briefs.py "$RUN_DIR"
