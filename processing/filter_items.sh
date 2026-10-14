#!/usr/bin/env bash
# Mechanical freshness filter: item JSONL on stdin (normally corpus.jsonl) ->
# eligible item JSONL on stdout, exclusion records in RUN_DIR/exclusions.jsonl.
# The 30-date window is as_of_date minus 29 days through as_of_date, UTC, inclusive.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" processing/filter_items.py "$RUN_DIR"
