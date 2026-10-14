#!/usr/bin/env bash
# Evidence store entry point. The ONLY component that reads or writes data/evidence/.
#
#   bash data/store.sh init                      create missing storage, no output
#   bash data/store.sh upsert RUN_DIR            item JSONL on stdin -> change JSONL on stdout
#   bash data/store.sh list                      latest version of every item, one per line
#   bash data/store.sh get ITEM_ID [VERSION_ID]  one item record (latest when version omitted)
#
# Exit 0 on success, 1 when a requested item is absent or storage fails, 2 on bad arguments/input.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_python
cd "$PIPELINE_ROOT"

cmd="${1:-}"
case "$cmd" in
  init|list)
    [ $# -eq 1 ] || die_invalid "usage: store.sh $cmd"
    exec "$PIPELINE_PYTHON" data/store.py "$cmd"
    ;;
  upsert)
    [ $# -eq 2 ] || die_invalid "usage: store.sh upsert RUN_DIR"
    RUN_DIR="$(require_run_dir "$2")" || exit $?
    exec "$PIPELINE_PYTHON" data/store.py upsert "$RUN_DIR"
    ;;
  get)
    [ $# -eq 2 ] || [ $# -eq 3 ] || die_invalid "usage: store.sh get ITEM_ID [VERSION_ID]"
    shift
    exec "$PIPELINE_PYTHON" data/store.py get "$@"
    ;;
  *)
    die_invalid "usage: store.sh {init|upsert RUN_DIR|list|get ITEM_ID [VERSION_ID]}"
    ;;
esac
