#!/usr/bin/env python3
"""Export package articles as paste-ready HTML for Substack.

    .venv/bin/python tools/export_substack_html.py runs/RUN_ID

Writes package/NN-article.html next to each NN-article.md. Open the HTML file in a
browser, select all, copy, and paste into a new Substack post: headings, links, bold
and lists survive the paste; the Sources list keeps its numbered references.
Also writes package/PUBLISHING_GUIDE.md with the click-by-click steps.
"""
from __future__ import annotations

import glob
import os
import sys

import markdown

STYLE = ("body{font-family:Georgia,serif;max-width:720px;margin:2rem auto;line-height:1.55;color:#111}"
         "h1{font-size:1.9rem}h2{font-size:1.3rem;margin-top:1.6rem}a{color:#1a5fb4}li{margin:.3rem 0}em{color:#444}")

GUIDE = """# Publishing guide for this package

Everything below is a manual step; the pipeline stops at this package by design.

## 1. Videos (Google Vids or HeyGen)
- Script: `NN-video-script.md` — one scene per `## N.` heading with **Visual**, **On-screen text** and **Narration**.
- HeyGen (UI): create an avatar video, add one scene per script scene, paste each *Narration* line as the
  script (drop the `[n]` markers; they are not read aloud), put *On-screen text* as a text overlay, pick a
  neutral background. Export 1080p MP4.
- HeyGen (API, optional): `HEYGEN_API_KEY=... .venv/bin/python tools/heygen_render.py runs/RUN_ID --avatar AVATAR_ID --voice VOICE_ID`
  renders `package/videos/NN.mp4` (list ids with `--list-avatars` / `--list-voices`).
- Google Vids: start from a blank video, one scene per script scene, use *Visual* as the slide design brief and
  *Narration* as the voice-over text (AI voice or record), *On-screen text* as the title element.
- Target length 3-5 minutes; the `Runtime target` line in each script estimates it at 150 words per minute.

## 2. Substack
- Open `NN-article.html` in a browser, select all (Cmd-A), copy, paste into a new post. Set the title from the
  first heading, remove the duplicated H1 if Substack keeps it, keep the *As of* line and the Sources section.
- Set the post to free / public, publish, copy the URL.

## 3. YouTube
- Upload the MP4 (public or unlisted). Title: the script title. Description: paste `NN-youtube-description.txt`
  after replacing `[substack link to add]` with the article URL. The numbered sources match the on-screen
  references.
- API alternative: `tools/youtube_upload.py` (needs a Google OAuth client JSON; see its docstring).

## 4. Record the links
- `.venv/bin/python tools/record_links.py runs/RUN_ID 01 --substack URL --youtube URL` (repeat per piece), or edit
  `publication_links.json` by hand, then `bash run.sh --package runs/RUN_ID` to refresh `summary.json`
  (links are preserved; nothing is regenerated).
- Add the video link to the Substack article and the article link to the YouTube description.
"""


def main(run_dir: str) -> int:
    pkg = os.path.join(run_dir, "package")
    if not os.path.isdir(pkg):
        print(f"no package directory in {run_dir}; run `bash run.sh --package {run_dir}` first", file=sys.stderr)
        return 1
    n = 0
    for md_path in sorted(glob.glob(os.path.join(pkg, "*-article.md"))):
        text = open(md_path, encoding="utf-8").read()
        body = markdown.markdown(text, extensions=["extra", "sane_lists"])
        title = text.splitlines()[0].lstrip("# ").strip()
        html = (f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{title}</title><style>{STYLE}</style></head>"
                f"<body>{body}</body></html>\n")
        out = md_path[:-3] + ".html"
        open(out, "w", encoding="utf-8").write(html)
        n += 1
        print(f"wrote {out}")
    open(os.path.join(pkg, "PUBLISHING_GUIDE.md"), "w", encoding="utf-8").write(GUIDE)
    print(f"wrote {os.path.join(pkg, 'PUBLISHING_GUIDE.md')}")
    return 0 if n else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: export_substack_html.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
