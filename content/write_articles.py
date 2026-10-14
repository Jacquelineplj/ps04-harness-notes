#!/usr/bin/env python3
"""Generate three article drafts from the briefs.

stdin: brief JSONL. stdout: manifest JSONL {piece_id, path, claim_ids, ...}.
Side effects: RUN_DIR/articles/01.md, 02.md, 03.md. Each draft keeps inline claim
markers such as [01-c1]; a Sources section resolving every claim to publisher,
title, date, link (with timestamps for media) and the exact passage is appended
mechanically so no citation depends on the model.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import evidence_passages, fmt_timestamp, markers_in, read_jsonl, source_notes_markdown  # noqa: E402
from lib.llm import LLMError, complete, stage_settings  # noqa: E402
from lib.receipt import Receipt  # noqa: E402

STAGE = "write_articles"
WORDS_MIN, WORDS_MAX = 600, 900
SCHEMA = {"type": "object", "properties": {"title": {"type": "string"}, "markdown": {"type": "string"}},
          "required": ["title", "markdown"], "additionalProperties": False}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def body_words(markdown: str) -> int:
    body = markdown.split("\n## Sources", 1)[0]
    body = re.sub(r"^#.*$", "", body, count=1, flags=re.M)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", body))


def render_evidence(brief: dict, items_by_id: dict) -> str:
    out = []
    for block in evidence_passages(brief, items_by_id):
        c = block["claim"]
        out.append(f"CLAIM {c['claim_id']} ({c['type']}): {c['statement']}")
        for e in block["entries"]:
            it = e["item"]
            if not it:
                continue
            where = f"{it.get('publisher_id')} | {it.get('kind')} | {it.get('title')} | {(it.get('published_at') or '?')[:10]}"
            if e["start_seconds"] is not None:
                where += f" | at {fmt_timestamp(e['start_seconds'])}"
            out.append(f"  evidence: {where}\n  passage: {e.get('passage')}\n  context: {e.get('context') or ''}")
    return "\n".join(out)


def footer(as_of: str) -> str:
    return (f"\n\n---\n*As of {as_of}. Drafted with AI assistance from the retained sources listed below; "
            f"selection, synthesis and wording were reviewed by a human editor before publication.*\n")


def main(run_dir: str) -> int:
    settings = stage_settings(STAGE, run_dir)
    receipt = Receipt(run_dir, STAGE, tools=[f"llm:{settings['provider']}"])
    briefs = []
    for n, line in enumerate(sys.stdin, 1):
        if line.strip():
            try:
                briefs.append(json.loads(line))
            except json.JSONDecodeError as exc:
                receipt.add_error(f"line {n}: malformed brief ({exc})")
                receipt.finish("invalid_input", input_count=n, output_count=0)
                return 2
    run = json.load(open(os.path.join(run_dir, "run.json"), encoding="utf-8"))
    items_by_id = {it["item_id"]: it for it in read_jsonl(os.path.join(run_dir, "eligible.jsonl"))}
    project = read(os.path.join(run_dir, "config", "project.json"))
    prompt = read(os.path.join(run_dir, "prompts", "write_articles.md"))
    system = f"PROJECT BRIEF (JSON):\n{project}\n\nINSTRUCTIONS:\n{prompt}\n\nRespond with JSON matching the schema: title and the full article markdown."
    os.makedirs(os.path.join(run_dir, "articles"), exist_ok=True)
    written = 0
    for brief in sorted(briefs, key=lambda b: b.get("piece_id", "")):
        pid = brief["piece_id"]
        claim_ids = [c["claim_id"] for c in brief.get("claims", [])]
        brief_view = {k: brief.get(k) for k in ("piece_id", "title", "question", "argument", "synthesis", "limitations")}
        brief_view["claims"] = [{"claim_id": c["claim_id"], "type": c["type"], "statement": c["statement"]} for c in brief.get("claims", [])]
        base_user = (f"As-of date: {run['as_of_date']}\n\nBRIEF (JSON):\n{json.dumps(brief_view, ensure_ascii=False, indent=1)}\n\n"
                     f"EVIDENCE PASSAGES (cite with the claim markers; do not invent beyond these):\n{render_evidence(brief, items_by_id)}")
        markdown, attempts, note = None, 0, ""
        while attempts < 2:
            attempts += 1
            user = base_user + (f"\n\nREVISION NOTE: {note}" if note else "")
            try:
                res = complete(system=system, user=user, schema=SCHEMA, stage=STAGE, run_dir=run_dir, label=f"article-{pid}-try{attempts}", settings=settings)
            except LLMError as exc:
                receipt.add_error(f"piece {pid}: {exc}")
                break
            receipt.add_model_usage(res["usage"])
            data = res["data"] or {}
            md = (data.get("markdown") or "").strip()
            title = (data.get("title") or brief.get("title") or f"Piece {pid}").strip()
            if not md.startswith("#"):
                md = f"# {title}\n\n{md}"
            words = body_words(md)
            used = [m for m in markers_in(md) if m in claim_ids]
            problems = []
            if words < WORDS_MIN - 50 or words > WORDS_MAX + 50:
                problems.append(f"body is {words} words; target {WORDS_MIN}-{WORDS_MAX}")
            if len(used) < max(3, len(claim_ids) // 2):
                problems.append(f"only {len(used)} of {len(claim_ids)} claims are cited with markers; cite every claim")
            markdown = md
            if not problems:
                break
            note = "; ".join(problems)
            receipt.add_error(f"piece {pid} attempt {attempts}: {note}", severity="warning")
        if markdown is None:
            continue
        markdown = markdown.rstrip() + footer(run["as_of_date"]) + "\n## Sources\n\n" + source_notes_markdown(brief, items_by_id) + "\n"
        path = os.path.join(run_dir, "articles", f"{pid}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(markdown)
        cited = [m for m in markers_in(markdown.split("\n## Sources", 1)[0]) if m in claim_ids]
        manifest = {"piece_id": pid, "path": path, "claim_ids": cited, "title": markdown.splitlines()[0].lstrip("# ").strip(),
                    "word_count": body_words(markdown), "uncited_claims": [c for c in claim_ids if c not in cited],
                    "model": settings["model"], "attempts": attempts}
        sys.stdout.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        written += 1
        print(f"write_articles: {pid}: {manifest['word_count']} words, {len(cited)}/{len(claim_ids)} claims cited", file=sys.stderr)
    status = "completed" if written == len(briefs) and not any(e for e in receipt.errors if e.get("severity") != "warning") else ("completed_with_errors" if written else "failed")
    receipt.finish(status, input_count=len(briefs), output_count=written)
    return 0 if written == len(briefs) and briefs else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: write_articles.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
