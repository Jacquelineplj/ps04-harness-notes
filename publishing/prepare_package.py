#!/usr/bin/env python3
"""Assemble the production package after human approval.

Checks: review.json exists and passed; approval.json exists with decision "approve",
reviewer, reviewed_at and the same review_id; the fingerprint recomputed now (by
invoking review/check_content.sh without saving its output) still equals the
approved review_id. Any failure lists what is missing or stale and exits 1.

Package contents (RUN_DIR/package/): NN-article.md and NN-video-script.md with claim
markers resolved to numbered references and a reference list, NN-sources.md (full
source notes), NN-youtube-description.txt, manifest.json (assets, piece ids, manual
steps), publication_links.json (preserved when it already exists) and MANUAL_STEPS.md.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import MARKER, abs_path, read_jsonl, source_notes_markdown  # noqa: E402
from lib.receipt import Receipt  # noqa: E402

STAGE = "prepare_package"
PIECES = ("01", "02", "03")
MANUAL_STEPS = [
    "Produce each video in Google Vids or HeyGen from package/NN-video-script.md (Visual/On-screen text/Narration per scene); an avatar is optional. Export MP4.",
    "Publish each package/NN-article.md on Substack with shareable (free) access; keep the Sources section and the AI-assistance line.",
    "Upload each video to YouTube (public or unlisted) using package/NN-youtube-description.txt as the description; add the Substack link to it.",
    "Add the YouTube link to the corresponding Substack article.",
    "Fill substack_url and youtube_url for every piece in package/publication_links.json; rerun `bash run.sh --package RUN_DIR` to refresh the summary (links are preserved).",
]


def now():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def renumber(markdown: str, numbering: dict) -> str:
    return MARKER.sub(lambda m: f"[{numbering.get(m.group(1), m.group(1))}]", markdown)


def main(run_dir: str) -> int:
    receipt = Receipt(run_dir, STAGE, tools=["python"])
    problems = []
    review_path = os.path.join(run_dir, "review.json")
    approval_path = os.path.join(run_dir, "approval.json")
    review = approval = None
    if not os.path.exists(review_path):
        problems.append("review.json missing: run review/check_content.sh first")
    else:
        review = json.load(open(review_path, encoding="utf-8"))
        if not review.get("passed"):
            problems.append("review.json has passed=false; repair the reported errors and rerun the checks")
    if not os.path.exists(approval_path):
        problems.append("approval.json missing: the human reviewer must record a decision")
    else:
        approval = json.load(open(approval_path, encoding="utf-8"))
        for k in ("review_id", "decision", "reviewer", "reviewed_at"):
            if not approval.get(k):
                problems.append(f"approval.json lacks {k}")
        if approval.get("decision") != "approve":
            problems.append(f"approval.json decision is {approval.get('decision')!r}, not 'approve'")
        if review and approval.get("review_id") != review.get("review_id"):
            problems.append("approval.json review_id does not match review.json (stale approval)")
    if not problems:
        proc = subprocess.run(["bash", "review/check_content.sh", run_dir], cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            problems.append(f"could not recompute the review fingerprint: {proc.stderr.strip()[:200]}")
        else:
            current = json.loads(proc.stdout)
            if current.get("review_id") != approval.get("review_id"):
                problems.append("reviewed inputs changed since approval (fingerprint differs); re-review and re-approve")
            if not current.get("passed"):
                problems.append("current checks no longer pass")
    if problems:
        for p in problems:
            receipt.add_error(p)
            print(f"prepare_package: {p}", file=sys.stderr)
        receipt.finish("failed", input_count=0, output_count=0, cost_usd=0.0, cost_is_estimate=False)
        return 1

    run = json.load(open(os.path.join(run_dir, "run.json"), encoding="utf-8"))
    briefs = {b["piece_id"]: b for b in read_jsonl(os.path.join(run_dir, "briefs.jsonl"))}
    arts = {m["piece_id"]: m for m in read_jsonl(os.path.join(run_dir, "articles.jsonl"))}
    scrs = {m["piece_id"]: m for m in read_jsonl(os.path.join(run_dir, "video_scripts.jsonl"))}
    items = {it["item_id"]: it for it in read_jsonl(os.path.join(run_dir, "eligible.jsonl"))}
    pkg = os.path.join(run_dir, "package")
    os.makedirs(pkg, exist_ok=True)
    pieces = []
    for pid in PIECES:
        b = briefs[pid]
        numbering = {c["claim_id"]: i for i, c in enumerate(b["claims"], 1)}
        notes = source_notes_markdown(b, items, numbered=numbering)
        article = open(abs_path(arts[pid]["path"]), encoding="utf-8").read()
        body, _, _ = article.partition("\n## Sources")
        article_out = renumber(body.rstrip(), numbering) + "\n\n## Sources\n\n" + notes + "\n"
        script = open(abs_path(scrs[pid]["path"]), encoding="utf-8").read()
        sbody, _, rest = script.partition("\n## Description")
        description = rest.split("\n## Sources", 1)[0].strip() if rest else ""
        script_out = renumber(sbody.rstrip(), numbering) + "\n\n## Sources\n\n" + notes + "\n"
        yt_desc = (f"{description}\n\nRead the full article: [substack link to add]\n\nSources (numbers match the on-screen references):\n" +
                   re.sub(r"\*\*|\*", "", notes) + f"\n\nAs of {run['as_of_date']}. AI-assisted script and presentation; sources were reviewed by a human editor.\n")
        sources_md = f"# Sources for piece {pid}: {b['title']}\n\nAs of {run['as_of_date']}. Numbers match the references in the article and script.\n\n" + notes + "\n"
        files = {"article": f"{pid}-article.md", "video_script": f"{pid}-video-script.md",
                 "sources": f"{pid}-sources.md", "youtube_description": f"{pid}-youtube-description.txt"}
        for key, content in (("article", article_out), ("video_script", script_out), ("sources", sources_md), ("youtube_description", yt_desc)):
            with open(os.path.join(pkg, files[key]), "w", encoding="utf-8") as fh:
                fh.write(content)
        pieces.append({"piece_id": pid, "title": b["title"], **{k: os.path.join(pkg, v) for k, v in files.items()},
                       "claim_count": len(b["claims"]), "evidence_items": b.get("evidence_items", [])})
    links_path = os.path.join(pkg, "publication_links.json")
    if os.path.exists(links_path):
        links = json.load(open(links_path, encoding="utf-8"))
    else:
        links = [{"piece_id": pid, "substack_url": None, "youtube_url": None} for pid in PIECES]
        with open(links_path, "w", encoding="utf-8") as fh:
            json.dump(links, fh, indent=2)
            fh.write("\n")
    with open(os.path.join(pkg, "MANUAL_STEPS.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# Manual steps remaining for run {run['run_id']}\n\nPreparing this package does not render videos or publish anything.\n\n")
        for i, s in enumerate(MANUAL_STEPS, 1):
            fh.write(f"{i}. {s}\n")
    manifest = {"run_id": run["run_id"], "as_of_date": run["as_of_date"], "packaged_at": now(),
                "review_id": approval["review_id"], "approved_by": approval["reviewer"], "approved_at": approval["reviewed_at"],
                "pieces": pieces, "publication_links": links_path, "manual_steps": MANUAL_STEPS,
                "note": "Videos are not rendered and nothing is published by this pipeline; see MANUAL_STEPS.md."}
    with open(os.path.join(pkg, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    sys.stdout.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    receipt.finish("completed", input_count=6, output_count=len(pieces) * 4 + 3, cost_usd=0.0, cost_is_estimate=False,
                   review_id=approval["review_id"])
    print(f"prepare_package: package ready in {pkg}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: prepare_package.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
