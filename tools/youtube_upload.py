#!/usr/bin/env python3
"""Upload the rendered videos to YouTube with the Data API and record the links.

One-time setup (your Google account, ~10 minutes):
  1. console.cloud.google.com -> create a project -> enable "YouTube Data API v3".
  2. OAuth consent screen (External, add yourself as a test user) -> Credentials ->
     "OAuth client ID" of type Desktop app -> download the JSON.
  3. Save it OUTSIDE the repo or as client_secret.json at the repo root (gitignored).

Run:
  YOUTUBE_CLIENT_SECRET=/path/client_secret.json .venv/bin/python tools/youtube_upload.py runs/RUN_ID [--privacy unlisted|public] [--pieces 01,02,03]

The first run opens a browser for consent and caches the token in youtube_token.json
(gitignored). Each piece uploads package/videos/NN.mp4 with the script title and
NN-youtube-description.txt (the Substack URL from publication_links.json is substituted
when present), then writes youtube_url into package/publication_links.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def credentials(secret_path: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    token_path = "youtube_token.json"
    creds = Credentials.from_authorized_user_file(token_path, SCOPES) if os.path.exists(token_path) else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES).run_local_server(port=0)
        open(token_path, "w").write(creds.to_json())
    return creds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--privacy", default="unlisted", choices=["unlisted", "public", "private"])
    ap.add_argument("--pieces", default="01,02,03")
    a = ap.parse_args()
    secret = os.environ.get("YOUTUBE_CLIENT_SECRET") or "client_secret.json"
    if not os.path.exists(secret):
        sys.exit("OAuth client JSON not found; set YOUTUBE_CLIENT_SECRET (see the docstring for the one-time setup)")
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    yt = build("youtube", "v3", credentials=credentials(secret))
    pkg = os.path.join(a.run_dir, "package")
    links_path = os.path.join(pkg, "publication_links.json")
    links = json.load(open(links_path))
    by_piece = {l["piece_id"]: l for l in links}
    for pid in a.pieces.split(","):
        mp4 = os.path.join(pkg, "videos", f"{pid}.mp4")
        if not os.path.exists(mp4):
            print(f"{pid}: {mp4} missing (render it first)", file=sys.stderr)
            continue
        title = open(os.path.join(pkg, f"{pid}-video-script.md"), encoding="utf-8").readline().lstrip("# ").strip()
        desc = open(os.path.join(pkg, f"{pid}-youtube-description.txt"), encoding="utf-8").read()
        sub = by_piece.get(pid, {}).get("substack_url")
        if sub:
            desc = desc.replace("[substack link to add]", sub)
        body = {"snippet": {"title": title[:100], "description": desc[:4900], "categoryId": "28"},
                "status": {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False}}
        req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(mp4, chunksize=-1, resumable=True))
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status:
                print(f"{pid}: uploading {int(status.progress() * 100)}%", file=sys.stderr)
        url = f"https://www.youtube.com/watch?v={resp['id']}"
        by_piece.setdefault(pid, {"piece_id": pid, "substack_url": None, "youtube_url": None})["youtube_url"] = url
        print(f"{pid}: {url}")
    json.dump([by_piece[p] for p in sorted(by_piece)], open(links_path, "w"), indent=2)
    open(links_path, "a").write("\n")
    print(f"links written to {links_path}; now run: bash run.sh --package {a.run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
