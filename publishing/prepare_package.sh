#!/usr/bin/env bash
# Publication handoff. Requires a passing current review and a matching human approval
# (RUN_DIR/approval.json). Verifies that the reviewed inputs are unchanged by recomputing
# the review fingerprint, then builds RUN_DIR/package/ and prints its manifest JSON.
# Exit 1 (with a list of what is missing or stale) when the package cannot be prepared.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"
RUN_DIR="$(require_run_dir "${1:-}")" || exit $?
exec "$PIPELINE_PYTHON" publishing/prepare_package.py "$RUN_DIR"
