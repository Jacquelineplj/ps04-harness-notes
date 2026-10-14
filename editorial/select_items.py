#!/usr/bin/env python3
"""Apply the snapshotted editorial policy to every eligible item through the model.

stdin: eligible item JSONL. stdout: one decision per item, in input order:
  {item_id, version_id, decision (accept|reject|defer), reason, piece_ids, ...extras}
Extras: perspective, credibility_notes, novelty, duplicate_of, decision_source
(`model`, or `fallback` when the model returned nothing usable for the item).
The policy, prompt and project brief are read from the run snapshot only.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import item_header, load_segments, load_text, render_segments  # noqa: E402
from lib.llm import LLMError, complete, stage_settings  # noqa: E402
from lib.receipt import Receipt  # noqa: E402

BATCH_SIZE = int(os.environ.get("SELECT_BATCH_SIZE", "6"))
HEAD_CHARS = 3000
PIECES = ("01", "02", "03")
STAGE = "select_items"

SCHEMA = {
    "type": "object",
    "properties": {
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "version_id": {"type": "string"},
                    "decision": {"type": "string", "enum": ["accept", "reject", "defer"]},
                    "reason": {"type": "string"},
                    "piece_ids": {"type": "array", "items": {"type": "string", "enum": ["01", "02", "03"]}},
                    "perspective": {"type": "string", "enum": ["research", "commercial", "practitioner", "mixed"]},
                    "credibility_notes": {"type": "string"},
                    "novelty": {"type": "string", "enum": ["new_development", "new_reporting_of_older_event", "recap_or_duplicate", "unclear"]},
                    "duplicate_of": {"type": ["string", "null"]},
                },
                "required": ["item_id", "version_id", "decision", "reason", "piece_ids", "perspective",
                             "credibility_notes", "novelty", "duplicate_of"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["decisions"],
    "additionalProperties": False,
}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def gist(item: dict) -> str:
    g = item.get("summary") or item.get("description") or ""
    if not g:
        g = load_text(item)[:300]
    g = " ".join(g.split())
    return g[:200]


def corpus_index(items: list) -> str:
    lines = []
    for it in items:
        lines.append(f"- {it['item_id']} | {it.get('publisher_id')} | {it.get('kind')} | {(it.get('published_at') or '?')[:10]} | "
                     f"{it.get('title')} | {gist(it)}")
    return "\n".join(lines)


def dossier(item: dict) -> str:
    parts = [item_header(item)]
    if item.get("segments_path"):
        segs = load_segments(item)
        n = len(segs)
        parts.append("Transcript opening:\n" + render_segments(segs, max_chars=1500))
        for frac in (0.3, 0.6, 0.85):
            idx = int(n * frac)
            if idx < n:
                parts.append(f"Transcript excerpt (~{int(frac * 100)}% in):\n" + render_segments(segs, max_chars=600, start=idx))
    else:
        text = load_text(item)
        head = text[:HEAD_CHARS]
        parts.append("Retained text opening:\n" + head + ("\n[... text continues ...]" if len(text) > HEAD_CHARS else ""))
    return "\n".join(parts)


def fallback(item: dict, note: str) -> dict:
    return {"item_id": item["item_id"], "version_id": item["version_id"], "decision": "defer",
            "reason": f"OPERATIONAL: {note}; deferred for human review, not an editorial judgement.",
            "piece_ids": [], "perspective": None, "credibility_notes": None, "novelty": None,
            "duplicate_of": None, "decision_source": "fallback"}


def normalise(item: dict, d: dict, errors: list) -> dict:
    out = {
        "item_id": item["item_id"],
        "version_id": item["version_id"],
        "decision": d.get("decision"),
        "reason": (d.get("reason") or "").strip(),
        "piece_ids": [p for p in (d.get("piece_ids") or []) if p in PIECES],
        "perspective": d.get("perspective"),
        "credibility_notes": d.get("credibility_notes"),
        "novelty": d.get("novelty"),
        "duplicate_of": d.get("duplicate_of") or None,
        "decision_source": "model",
    }
    if out["decision"] not in ("accept", "reject", "defer") or not out["reason"]:
        errors.append(f"{item['item_id']}: unusable decision from model")
        return fallback(item, "model returned an unusable decision")
    if out["decision"] == "accept" and not out["piece_ids"]:
        out["decision"] = "defer"
        out["reason"] = "OPERATIONAL: model accepted the item without naming a piece. Model reason: " + out["reason"]
        out["decision_source"] = "model_unassigned"
    if out["decision"] != "accept":
        out["piece_ids"] = []
    out["piece_ids"] = sorted(set(out["piece_ids"]))
    return out


def main(run_dir: str) -> int:
    settings = stage_settings(STAGE, run_dir)
    receipt = Receipt(run_dir, STAGE, tools=[f"llm:{settings['provider']}"])
    items = []
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            if not rec.get("item_id") or not rec.get("version_id"):
                raise ValueError("missing item_id/version_id")
        except (json.JSONDecodeError, ValueError, AttributeError) as exc:
            receipt.add_error(f"line {n}: malformed eligible record ({exc})")
            receipt.finish("invalid_input", input_count=n, output_count=0)
            print(f"select_items: line {n}: malformed input: {exc}", file=sys.stderr)
            return 2
        items.append(rec)
    if not items:
        receipt.finish("completed", input_count=0, output_count=0, cost_usd=0.0, cost_is_estimate=False)
        print("select_items: no eligible items", file=sys.stderr)
        return 0
    project = read(os.path.join(run_dir, "config", "project.json"))
    policy = read(os.path.join(run_dir, "config", "editorial_policy.md"))
    prompt = read(os.path.join(run_dir, "prompts", "select_items.md"))
    system = (f"PROJECT BRIEF (JSON):\n{project}\n\nEDITORIAL POLICY:\n{policy}\n\nINSTRUCTIONS:\n{prompt}\n\n"
              "Respond with JSON matching the provided schema and nothing else.")
    index = corpus_index(items)
    decisions = []
    counts = {"accept": 0, "reject": 0, "defer": 0}
    failed_batches = 0
    for b in range(0, len(items), BATCH_SIZE):
        batch = items[b:b + BATCH_SIZE]
        user = (f"CORPUS INDEX ({len(items)} eligible items in this run; use it to spot reposts and duplicates):\n{index}\n\n"
                f"BATCH ({len(batch)} items; return exactly one decision per item, in this order):\n\n" +
                "\n\n=====\n\n".join(f"ITEM {i + 1}\n{dossier(it)}" for i, it in enumerate(batch)))
        by_id = {}
        try:
            res = complete(system=system, user=user, schema=SCHEMA, stage=STAGE, run_dir=run_dir,
                           label=f"batch{b // BATCH_SIZE + 1}", settings=settings)
            receipt.add_model_usage(res["usage"])
            for d in (res["data"] or {}).get("decisions", []):
                if isinstance(d, dict) and d.get("item_id"):
                    by_id.setdefault(d["item_id"], d)
        except LLMError as exc:
            failed_batches += 1
            receipt.add_error(f"batch {b // BATCH_SIZE + 1}: {exc}")
            print(f"select_items: batch {b // BATCH_SIZE + 1} failed: {exc}", file=sys.stderr)
        for it in batch:
            d = by_id.get(it["item_id"])
            if d is None:
                errs = []
                dec = fallback(it, "no decision returned by the model for this item")
                receipt.add_error(f"{it['item_id']}: no decision returned; fallback defer")
            else:
                errs = []
                dec = normalise(it, d, errs)
                for e in errs:
                    receipt.add_error(e)
            dec["model"] = settings["model"]
            counts[dec["decision"]] += 1
            decisions.append(dec)
            sys.stdout.write(json.dumps(dec, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        print(f"select_items: batch {b // BATCH_SIZE + 1}: {len(batch)} items decided", file=sys.stderr)
    status = "completed" if not receipt.errors else "completed_with_errors"
    if failed_batches:
        status = "completed_with_errors"
    receipt.finish(status, input_count=len(items), output_count=len(decisions), decisions=counts,
                   batches=(len(items) + BATCH_SIZE - 1) // BATCH_SIZE, failed_batches=failed_batches,
                   fallback_decisions=sum(1 for d in decisions if d["decision_source"] != "model"))
    print(f"select_items: {counts}", file=sys.stderr)
    return 1 if failed_batches else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: select_items.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
