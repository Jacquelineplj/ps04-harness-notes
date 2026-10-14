#!/usr/bin/env python3
"""Record publication links for a piece, then refresh the package summary.

    .venv/bin/python tools/record_links.py runs/RUN_ID 01 --substack URL [--youtube URL]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("piece_id", choices=["01", "02", "03"])
    ap.add_argument("--substack")
    ap.add_argument("--youtube")
    ap.add_argument("--no-repackage", action="store_true")
    a = ap.parse_args()
    path = os.path.join(a.run_dir, "package", "publication_links.json")
    if not os.path.exists(path):
        sys.exit(f"{path} missing: run `bash run.sh --package {a.run_dir}` first")
    links = json.load(open(path))
    for l in links:
        if l["piece_id"] == a.piece_id:
            if a.substack:
                l["substack_url"] = a.substack
            if a.youtube:
                l["youtube_url"] = a.youtube
    json.dump(links, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps(links, indent=2))
    if not a.no_repackage:
        return subprocess.call(["bash", "run.sh", "--package", a.run_dir], stdout=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
