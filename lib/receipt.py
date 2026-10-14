#!/usr/bin/env python3
"""Receipt writer shared by every stage.

Each invocation of a stage writes one uniquely named JSON receipt under
RUN_DIR/logs/. Earlier receipts are never overwritten. Receipts never contain
credentials or prompt text; only counts, timings, tools, models, costs, errors.

Python usage:
    r = Receipt(run_dir, "fetch_feeds", tools=["feedparser"])
    r.add_error("feed timed out", source_id="x")
    r.finish("completed_with_errors", input_count=3, output_count=2)

Shell usage (see lib/common.sh write_receipt):
    python lib/receipt.py RUN_DIR STAGE STATUS STARTED_AT [options]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

STATUSES = {"completed", "completed_with_errors", "failed", "invalid_input", "skipped"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


class Receipt:
    def __init__(self, run_dir: str, stage: str, tools=None, started_at: str | None = None):
        self.run_dir = run_dir
        self.stage = stage
        self.started_at = started_at or utc_now()
        self.tools = list(tools or [])
        self.models = []  # {provider, model, calls, input_tokens, output_tokens, cost_usd, cost_is_estimate}
        self.errors = []
        self.extra = {}

    def add_tool(self, name: str):
        if name and name not in self.tools:
            self.tools.append(name)

    def add_error(self, message: str, **fields):
        err = {"message": str(message)}
        err.update({k: v for k, v in fields.items() if v is not None})
        self.errors.append(err)

    def add_model_usage(self, usage: dict):
        """usage: {provider, model, input_tokens, output_tokens, cost_usd, cost_is_estimate}"""
        key = (usage.get("provider"), usage.get("model"))
        for m in self.models:
            if (m["provider"], m["model"]) == key:
                m["calls"] += 1
                m["input_tokens"] += int(usage.get("input_tokens") or 0)
                m["output_tokens"] += int(usage.get("output_tokens") or 0)
                if usage.get("cost_usd") is not None:
                    m["cost_usd"] = (m["cost_usd"] or 0.0) + float(usage["cost_usd"])
                if usage.get("cost_is_estimate"):
                    m["cost_is_estimate"] = True
                return
        self.models.append({
            "provider": usage.get("provider"),
            "model": usage.get("model"),
            "calls": 1,
            "input_tokens": int(usage.get("input_tokens") or 0),
            "output_tokens": int(usage.get("output_tokens") or 0),
            "cost_usd": usage.get("cost_usd"),
            "cost_is_estimate": bool(usage.get("cost_is_estimate")),
        })

    def total_cost(self):
        """Returns (cost_usd or None, is_estimate). None when any model cost is unknown."""
        if not self.models:
            return 0.0, False
        total, est = 0.0, False
        for m in self.models:
            if m.get("cost_usd") is None:
                return None, est
            total += float(m["cost_usd"])
            est = est or bool(m.get("cost_is_estimate"))
        return round(total, 6), est

    def finish(self, status: str, input_count=None, output_count=None, cost_usd="auto",
               cost_is_estimate=None, **extra) -> str:
        if status not in STATUSES:
            raise ValueError(f"unknown receipt status {status}")
        finished = utc_now()
        if cost_usd == "auto":
            cost_usd, auto_est = self.total_cost()
            if cost_is_estimate is None:
                cost_is_estimate = auto_est
        self.extra.update(extra)
        record = {
            "stage": self.stage,
            "status": status,
            "run_dir": self.run_dir,
            "input_count": input_count,
            "output_count": output_count,
            "started_at": self.started_at,
            "finished_at": finished,
            "elapsed_seconds": _elapsed(self.started_at, finished),
            "tools": self.tools,
            "models": self.models,
            "cost_usd": cost_usd,
            "cost_is_estimate": cost_is_estimate,
            "errors": self.errors,
            "extra": self.extra,
        }
        return write_record(self.run_dir, self.stage, record)


def _elapsed(start: str, end: str):
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        return round((_dt.datetime.strptime(end, fmt) - _dt.datetime.strptime(start, fmt)).total_seconds(), 3)
    except Exception:
        return None


def write_record(run_dir: str, stage: str, record: dict) -> str:
    logs = os.path.join(run_dir, "logs")
    os.makedirs(logs, exist_ok=True)
    path = os.path.join(logs, f"{stage}-{_stamp()}-{os.getpid()}.json")
    while os.path.exists(path):  # uniqueness even for sub-microsecond reruns
        path = os.path.join(logs, f"{stage}-{_stamp()}-{os.getpid()}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="write a stage receipt")
    ap.add_argument("run_dir")
    ap.add_argument("stage")
    ap.add_argument("status", choices=sorted(STATUSES))
    ap.add_argument("started_at")
    ap.add_argument("--input-count", type=int, default=None)
    ap.add_argument("--output-count", type=int, default=None)
    ap.add_argument("--tools", default="")
    ap.add_argument("--error", action="append", default=[])
    ap.add_argument("--cost-usd", default=None)
    ap.add_argument("--cost-is-estimate", action="store_true")
    ap.add_argument("--extra-json", default="{}")
    args = ap.parse_args(argv)
    r = Receipt(args.run_dir, args.stage, tools=[t for t in args.tools.split(",") if t], started_at=args.started_at)
    for e in args.error:
        r.add_error(e)
    try:
        extra = json.loads(args.extra_json) if args.extra_json else {}
    except json.JSONDecodeError as exc:
        print(f"receipt: invalid --extra-json: {exc}", file=sys.stderr)
        return 2
    cost = None if args.cost_usd in (None, "", "null") else float(args.cost_usd)
    path = r.finish(args.status, input_count=args.input_count, output_count=args.output_count,
                    cost_usd=cost, cost_is_estimate=(args.cost_is_estimate if cost is not None else None), **extra)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
