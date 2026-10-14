#!/usr/bin/env bash
# Mechanical content checks. Emits one JSON object (review_id, passed, issues, ...) on
# stdout; the caller saves it as RUN_DIR/review.json. Exit 0 whenever an assessment
# completed (even when passed is false); 1 when the assessment could not run; 2 on bad arguments.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" review/check_content.py "$RUN_DIR"
