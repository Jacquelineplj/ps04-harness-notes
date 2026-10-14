#!/usr/bin/env python3
"""Persistent evidence index behind data/store.sh (SQLite).

Layout: data/evidence/evidence.sqlite (override the directory with EVIDENCE_DIR
for disposable tests only).

  items(item_id PK, latest_version_id, first_seen_at, first_run_id, updated_at)
  versions(item_id, version_id, record_json, first_seen_at, first_run_id, PK(item_id, version_id))
  observations(id, item_id, version_id, run_id, retrieved_at, change, observed_at)

Change semantics for `upsert` (one change record per input record, input order):
  new        the item_id has never been stored
  changed    the item exists but this version_id is not its latest version
             (a brand-new version, or an older version observed again - the
             latest pointer follows what was observed)
  unchanged  the version_id is already the latest version; only an observation
             row is added, so refreshed retrieval timestamps never create versions

version_id values are opaque strings supplied by extract_content.sh.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sqlite3
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.receipt import Receipt  # noqa: E402

EVIDENCE_DIR = os.environ.get("EVIDENCE_DIR") or os.path.join(ROOT, "data", "evidence")
DB_PATH = os.path.join(EVIDENCE_DIR, "evidence.sqlite")

REQUIRED = ("item_id", "source_id", "publisher_id", "kind", "title", "url", "published_at",
            "retrieved_at", "media_url", "version_id", "text_path", "segments_path")
KINDS = ("feed", "youtube", "podcast")

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  item_id TEXT PRIMARY KEY,
  latest_version_id TEXT NOT NULL,
  first_seen_at TEXT NOT NULL,
  first_run_id TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
  item_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  record_json TEXT NOT NULL,
  first_seen_at TEXT NOT NULL,
  first_run_id TEXT,
  PRIMARY KEY (item_id, version_id)
);
CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  run_id TEXT,
  retrieved_at TEXT,
  change TEXT NOT NULL,
  observed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_obs_item ON observations(item_id, version_id);
"""


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def err(msg: str):
    print(f"store: {msg}", file=sys.stderr)


def connect(create: bool) -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        if not create:
            err(f"evidence store not initialised at {DB_PATH}; run `bash data/store.sh init`")
            sys.exit(1)
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def cmd_init() -> int:
    connect(create=True).close()
    readme = os.path.join(EVIDENCE_DIR, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as fh:
            fh.write("# Evidence index\n\nSQLite database `evidence.sqlite` managed only by `data/store.sh`.\n"
                     "Tables: items (latest pointer), versions (every retained version with its first run), "
                     "observations (every time a run saw an item version).\n"
                     "Retained text and transcript assets live in `data/assets/`; original media in `data/media/`.\n")
    return 0


def validate(rec: dict, line_no: int):
    if not isinstance(rec, dict):
        return f"line {line_no}: record is not an object"
    for k in REQUIRED:
        if k not in rec:
            return f"line {line_no}: missing field {k!r}"
    for k in ("item_id", "source_id", "publisher_id", "kind", "title", "url", "retrieved_at", "version_id", "text_path"):
        if not isinstance(rec.get(k), str) or not rec[k]:
            return f"line {line_no}: field {k!r} must be a nonempty string"
    if rec["kind"] not in KINDS:
        return f"line {line_no}: kind {rec['kind']!r} not in {KINDS}"
    if rec.get("published_at") is not None and not isinstance(rec["published_at"], str):
        return f"line {line_no}: published_at must be a string or null"
    return None


def cmd_upsert(run_dir: str) -> int:
    with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as fh:
        run_id = json.load(fh).get("run_id")
    receipt = Receipt(run_dir, "store_upsert", tools=["sqlite3"])
    conn = connect(create=True)
    counts = {"new": 0, "changed": 0, "unchanged": 0}
    n_in = 0
    rc = 0
    try:
        for line_no, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line:
                continue
            n_in += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                receipt.add_error(f"line {line_no}: malformed JSON ({exc})")
                err(f"line {line_no}: malformed JSON: {exc}")
                rc = 2
                break
            problem = validate(rec, line_no)
            if problem:
                receipt.add_error(problem)
                err(problem)
                rc = 2
                break
            change = apply_record(conn, rec, run_id)
            counts[change] += 1
            sys.stdout.write(json.dumps({"item_id": rec["item_id"], "version_id": rec["version_id"], "change": change}) + "\n")
            sys.stdout.flush()
        conn.commit()
    finally:
        conn.close()
        status = "completed" if rc == 0 else "invalid_input"
        receipt.finish(status, input_count=n_in, output_count=sum(counts.values()), cost_usd=0.0,
                       cost_is_estimate=False, changes=counts, run_id=run_id, evidence_db=os.path.relpath(DB_PATH, ROOT))
    return rc


def apply_record(conn: sqlite3.Connection, rec: dict, run_id: str) -> str:
    ts = now()
    item_id, version_id = rec["item_id"], rec["version_id"]
    row = conn.execute("SELECT latest_version_id FROM items WHERE item_id = ?", (item_id,)).fetchone()
    if row is None:
        change = "new"
        conn.execute("INSERT INTO versions(item_id, version_id, record_json, first_seen_at, first_run_id) VALUES (?,?,?,?,?)",
                     (item_id, version_id, json.dumps(rec, ensure_ascii=False, sort_keys=True), ts, run_id))
        conn.execute("INSERT INTO items(item_id, latest_version_id, first_seen_at, first_run_id, updated_at) VALUES (?,?,?,?,?)",
                     (item_id, version_id, ts, run_id, ts))
    elif row[0] == version_id:
        change = "unchanged"
    else:
        change = "changed"
        exists = conn.execute("SELECT 1 FROM versions WHERE item_id = ? AND version_id = ?", (item_id, version_id)).fetchone()
        if not exists:
            conn.execute("INSERT INTO versions(item_id, version_id, record_json, first_seen_at, first_run_id) VALUES (?,?,?,?,?)",
                         (item_id, version_id, json.dumps(rec, ensure_ascii=False, sort_keys=True), ts, run_id))
        conn.execute("UPDATE items SET latest_version_id = ?, updated_at = ? WHERE item_id = ?", (version_id, ts, item_id))
    conn.execute("INSERT INTO observations(item_id, version_id, run_id, retrieved_at, change, observed_at) VALUES (?,?,?,?,?,?)",
                 (item_id, version_id, run_id, rec.get("retrieved_at"), change, ts))
    return change


def cmd_list() -> int:
    conn = connect(create=False)
    rows = conn.execute(
        "SELECT v.record_json FROM items i JOIN versions v ON v.item_id = i.item_id AND v.version_id = i.latest_version_id "
        "ORDER BY i.item_id").fetchall()
    for (record_json,) in rows:
        sys.stdout.write(record_json + "\n")
    conn.close()
    run_dir = os.environ.get("RUN_DIR")
    if run_dir and os.path.isdir(run_dir):
        Receipt(run_dir, "store_list", tools=["sqlite3"]).finish("completed", input_count=0, output_count=len(rows),
                                                                 cost_usd=0.0, cost_is_estimate=False)
    return 0


def cmd_get(item_id: str, version_id: str | None) -> int:
    conn = connect(create=False)
    if version_id:
        row = conn.execute("SELECT record_json FROM versions WHERE item_id = ? AND version_id = ?", (item_id, version_id)).fetchone()
    else:
        row = conn.execute(
            "SELECT v.record_json FROM items i JOIN versions v ON v.item_id = i.item_id AND v.version_id = i.latest_version_id "
            "WHERE i.item_id = ?", (item_id,)).fetchone()
    conn.close()
    if row is None:
        err(f"not found: item_id={item_id} version_id={version_id or 'latest'}")
        return 1
    sys.stdout.write(row[0] + "\n")
    return 0


def main(argv) -> int:
    if not argv:
        err("missing subcommand")
        return 2
    cmd, args = argv[0], argv[1:]
    if cmd == "init" and not args:
        return cmd_init()
    if cmd == "upsert" and len(args) == 1:
        return cmd_upsert(args[0])
    if cmd == "list" and not args:
        return cmd_list()
    if cmd == "get" and 1 <= len(args) <= 2:
        return cmd_get(args[0], args[1] if len(args) == 2 else None)
    err(f"bad arguments: {argv}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
