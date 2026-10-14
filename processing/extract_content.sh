#!/usr/bin/env bash
# Content extraction: candidate JSONL on stdin -> normalized item JSONL on stdout.
# Retains text and transcript segments under data/assets/ and original media under
# data/media/. Reuses stored extraction results through data/store.sh when the
# underlying material is unchanged. Inaccessible or unprocessable items are reported
# in the receipt (exit 0 unless nothing could be processed; exit 2 on malformed input).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" processing/extract_content.py "$RUN_DIR"
