#!/usr/bin/env bash
# Content generator entry point (write_video_scripts). Brief JSONL on stdin -> manifest JSONL on stdout
# plus Markdown drafts under RUN_DIR.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" content/write_video_scripts.py "$RUN_DIR"
