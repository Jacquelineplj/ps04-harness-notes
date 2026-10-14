#!/usr/bin/env python3
"""Generate three audience-facing video scripts from the same briefs.

stdin: brief JSONL. stdout: manifest JSONL. Side effects: RUN_DIR/video_scripts/NN.md.
The finished article draft (when present) is supplied alongside the brief so the
script makes the same factual claims; scripts cite the same claim markers and a
Sources section plus a YouTube description block are appended mechanically.
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

STAGE = "write_video_scripts"
NARR_MIN, NARR_MAX = 450, 750
SCHEMA = {"type": "object",
          "properties": {"title": {"type": "string"}, "markdown": {"type": "string"}, "description": {"type": "string"}},
          "required": ["title", "markdown", "description"], "additionalProperties": False}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def narration_words(markdown: str) -> int:
    n = 0
    for line in markdown.split("\n## Sources", 1)[0].splitlines():
        s = line.strip()
        if s.lower().startswith(("narration:", "**narration:**", "- narration:")):
            s = re.sub(r"^\W*narration:\**\s*", "", s, flags=re.I)
            n += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", re.sub(r"\[\d\d-c\d+\]", "", s)))
    return n


def render_evidence(brief: dict, items_by_id: dict) -> str:
    out = []
    for block in evidence_passages(brief, items_by_id, context_chars=300):
        c = block["claim"]
        out.append(f"CLAIM {c['claim_id']} ({c['type']}): {c['statement']}")
        for e in block["entries"]:
            it = e["item"]
            if not it:
                continue
            where = f"{it.get('publisher_id')} | {it.get('kind')} | {it.get('title')} | {(it.get('published_at') or '?')[:10]}"
            if e["start_seconds"] is not None:
                where += f" | at {fmt_timestamp(e['start_seconds'])}"
            out.append(f"  evidence: {where}\n  passage: {e.get('passage')}")
    return "\n".join(out)


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
    prompt = read(os.path.join(run_dir, "prompts", "write_video_scripts.md"))
    system = (f"PROJECT BRIEF (JSON):\n{project}\n\nINSTRUCTIONS:\n{prompt}\n\n"
              "Respond with JSON matching the schema: title, the full script markdown, and the YouTube description.")
    os.makedirs(os.path.join(run_dir, "video_scripts"), exist_ok=True)
    written = 0
    for brief in sorted(briefs, key=lambda b: b.get("piece_id", "")):
        pid = brief["piece_id"]
        claim_ids = [c["claim_id"] for c in brief.get("claims", [])]
        article_path = os.path.join(run_dir, "articles", f"{pid}.md")
        article = read(article_path).split("\n## Sources", 1)[0] if os.path.exists(article_path) else None
        brief_view = {k: brief.get(k) for k in ("piece_id", "title", "question", "argument", "synthesis", "limitations")}
        brief_view["claims"] = [{"claim_id": c["claim_id"], "type": c["type"], "statement": c["statement"]} for c in brief.get("claims", [])]
        base_user = (f"As-of date: {run['as_of_date']}\n\nBRIEF (JSON):\n{json.dumps(brief_view, ensure_ascii=False, indent=1)}\n\n"
                     f"EVIDENCE PASSAGES:\n{render_evidence(brief, items_by_id)}\n\n" +
                     (f"PUBLISHED ARTICLE DRAFT (the script must make the same claims, no new facts):\n{article}" if article else ""))
        markdown, description, attempts, note = None, "", 0, ""
        while attempts < 2:
            attempts += 1
            user = base_user + (f"\n\nREVISION NOTE: {note}" if note else "")
            try:
                res = complete(system=system, user=user, schema=SCHEMA, stage=STAGE, run_dir=run_dir, label=f"script-{pid}-try{attempts}", settings=settings)
            except LLMError as exc:
                receipt.add_error(f"piece {pid}: {exc}")
                break
            receipt.add_model_usage(res["usage"])
            data = res["data"] or {}
            md = (data.get("markdown") or "").strip()
            title = (data.get("title") or brief.get("title") or f"Piece {pid}").strip()
            description = (data.get("description") or "").strip()
            if not md.startswith("#"):
                md = f"# {title}\n\n{md}"
            words = narration_words(md)
            used = [m for m in markers_in(md) if m in claim_ids]
            problems = []
            if words < NARR_MIN - 50 or words > NARR_MAX + 50:
                problems.append(f"narration is {words} words; target {NARR_MIN}-{NARR_MAX} (3-5 minutes)")
            if len(used) < 3:
                problems.append(f"only {len(used)} claims cited in narration; cite the claims you use")
            markdown = md
            if not problems:
                break
            note = "; ".join(problems)
            receipt.add_error(f"piece {pid} attempt {attempts}: {note}", severity="warning")
        if markdown is None:
            continue
        words = narration_words(markdown)
        markdown = (markdown.rstrip() + f"\n\n---\n*Estimated runtime: {words / 150:.1f} minutes at 150 words per minute. "
                    f"As of {run['as_of_date']}. AI-assisted script from reviewed sources; the presenter may be an AI avatar.*\n"
                    f"\n## Description\n\n{description}\n\n## Sources\n\n" + source_notes_markdown(brief, items_by_id) + "\n")
        path = os.path.join(run_dir, "video_scripts", f"{pid}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(markdown)
        cited = [m for m in markers_in(markdown.split("\n## Description", 1)[0]) if m in claim_ids]
        manifest = {"piece_id": pid, "path": path, "claim_ids": cited, "title": markdown.splitlines()[0].lstrip("# ").strip(),
                    "narration_words": words, "estimated_minutes": round(words / 150, 1), "model": settings["model"], "attempts": attempts}
        sys.stdout.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        written += 1
        print(f"write_video_scripts: {pid}: {words} narration words (~{words / 150:.1f} min), {len(cited)} claims cited", file=sys.stderr)
    status = "completed" if written == len(briefs) and not any(e for e in receipt.errors if e.get("severity") != "warning") else ("completed_with_errors" if written else "failed")
    receipt.finish(status, input_count=len(briefs), output_count=written)
    return 0 if written == len(briefs) and briefs else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: write_video_scripts.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
