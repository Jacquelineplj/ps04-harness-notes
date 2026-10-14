#!/usr/bin/env python3
"""Date-window eligibility check (no editorial judgement here).

Reads item JSONL on stdin, writes eligible items to stdout and exclusion records
(item_id, version_id, reason, detail) to RUN_DIR/exclusions.jsonl.
Reasons: outside_window, unknown_date, future_date, invalid_date.
Exit 2 when a stdin line is not valid JSON.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

from dateutil import parser as dateparser

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.receipt import Receipt  # noqa: E402

WINDOW_DAYS = 30


def to_utc_date(value: str):
    dt = dateparser.isoparse(value) if "T" in value or value.count("-") == 2 and len(value) >= 10 else dateparser.parse(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc).date()


def classify(published_at, as_of: _dt.date, start: _dt.date):
    if published_at is None:
        return "unknown_date", "published_at is null"
    if not isinstance(published_at, str) or not published_at.strip():
        return "invalid_date", f"published_at is not a date string: {published_at!r}"
    try:
        d = to_utc_date(published_at.strip())
    except (ValueError, OverflowError, TypeError) as exc:
        return "invalid_date", f"could not parse {published_at!r}: {exc}"
    if d > as_of:
        return "future_date", f"{d.isoformat()} is after as_of_date {as_of.isoformat()}"
    if d < start:
        return "outside_window", f"{d.isoformat()} is before window start {start.isoformat()}"
    return None, d.isoformat()


def main(run_dir: str) -> int:
    with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as fh:
        run = json.load(fh)
    as_of = _dt.date.fromisoformat(run["as_of_date"])
    start = as_of - _dt.timedelta(days=WINDOW_DAYS - 1)
    receipt = Receipt(run_dir, "filter_items", tools=["python-dateutil"])
    reasons = {"outside_window": 0, "unknown_date": 0, "future_date": 0, "invalid_date": 0}
    n_in = n_ok = 0
    rc = 0
    exclusions_path = os.path.join(run_dir, "exclusions.jsonl")
    with open(exclusions_path, "w", encoding="utf-8") as ex:
        for line_no, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line:
                continue
            n_in += 1
            try:
                rec = json.loads(line)
                if not isinstance(rec, dict) or "item_id" not in rec:
                    raise ValueError("record is not an item object")
            except (json.JSONDecodeError, ValueError) as exc:
                msg = f"line {line_no}: malformed input ({exc})"
                print(f"filter_items: {msg}", file=sys.stderr)
                receipt.add_error(msg)
                rc = 2  # malformed input is reported after the remaining records are processed
                continue
            reason, detail = classify(rec.get("published_at"), as_of, start)
            if reason is None:
                n_ok += 1
                sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            else:
                reasons[reason] += 1
                ex.write(json.dumps({"item_id": rec["item_id"], "version_id": rec.get("version_id"),
                                     "reason": reason, "detail": detail}, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    receipt.finish("completed" if rc == 0 else "invalid_input", input_count=n_in, output_count=n_ok,
                   cost_usd=0.0, cost_is_estimate=False, as_of_date=as_of.isoformat(),
                   window_start=start.isoformat(), window_end=as_of.isoformat(), excluded=sum(reasons.values()),
                   exclusion_reasons=reasons)
    print(f"filter_items: window {start} .. {as_of}: {n_ok} eligible, {sum(reasons.values())} excluded {reasons}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: filter_items.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
