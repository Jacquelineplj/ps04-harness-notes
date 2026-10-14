#!/usr/bin/env python3
"""Render the package video scripts as HeyGen avatar videos through the HeyGen API.

    HEYGEN_API_KEY=... .venv/bin/python tools/heygen_render.py runs/RUN_ID --list-avatars
    HEYGEN_API_KEY=... .venv/bin/python tools/heygen_render.py runs/RUN_ID --list-voices
    HEYGEN_API_KEY=... .venv/bin/python tools/heygen_render.py runs/RUN_ID --avatar AVATAR_ID --voice VOICE_ID [--pieces 01,02]

One HeyGen video per script; one HeyGen scene per script scene, using the scene's
Narration (claim markers removed) as the spoken text. Results are polled and the MP4s
are downloaded to RUN_DIR/package/videos/NN.mp4 (ignored by Git); a render log with
video ids is written next to them. The key is read from the environment only.

Endpoints (HeyGen public API v2; the script prints the API's own error text if a
request shape is rejected, so a plan or API change is visible immediately):
  GET  https://api.heygen.com/v2/avatars            list avatars  (data.avatars[].avatar_id)
  GET  https://api.heygen.com/v2/voices             list voices   (data.voices[].voice_id)
  POST https://api.heygen.com/v2/video/generate     create video  (data.video_id)
  GET  https://api.heygen.com/v1/video_status.get   poll          (data.status, data.video_url)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import httpx

API = "https://api.heygen.com"
MARK = re.compile(r"\s*\[\d+\]")


def key() -> str:
    k = os.environ.get("HEYGEN_API_KEY")
    if not k:
        sys.exit("HEYGEN_API_KEY is not set (export it in your shell; never write it to a file in the repo)")
    return k


def client() -> httpx.Client:
    return httpx.Client(base_url=API, headers={"X-Api-Key": key(), "Accept": "application/json"}, timeout=120)


def scenes(script_path: str) -> list:
    out, cur = [], {}
    for line in open(script_path, encoding="utf-8"):
        s = line.strip()
        if s.startswith("## Sources") or s.startswith("## Description"):
            break
        m = re.match(r"^(?:#{2,3}\s*|\*\*)\s*(?:scene\s*)?\d+[.)]\s*(.*?)\**\s*$", s, flags=re.I)
        if m:
            if cur.get("narration"):
                out.append(cur)
            cur = {"title": m.group(1).strip() or f"Scene {len(out) + 1}"}
        for label in ("Visual", "On-screen text", "Narration"):
            mm = re.match(rf"^\**{label}:\**\s*(.*)$", s, flags=re.I)
            if mm:
                cur[label.lower().replace(" ", "_").replace("-", "_")] = mm.group(1).strip()
    if cur.get("narration"):
        out.append(cur)
    for i, sc in enumerate(out, 1):
        sc.setdefault("title", f"Scene {i}")
        sc["narration"] = MARK.sub("", sc["narration"]).strip()
    return out


def show(resp: httpx.Response):
    try:
        body = resp.json()
    except ValueError:
        body = resp.text[:500]
    if resp.status_code >= 400 or (isinstance(body, dict) and body.get("error")):
        sys.exit(f"HeyGen API error {resp.status_code}: {json.dumps(body)[:800]}")
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--list-avatars", action="store_true")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--avatar")
    ap.add_argument("--voice")
    ap.add_argument("--pieces", default="01,02,03")
    ap.add_argument("--background", default="#0b1020")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    a = ap.parse_args()
    with client() as c:
        if a.list_avatars:
            data = show(c.get("/v2/avatars"))
            for av in (data.get("data") or {}).get("avatars", [])[:200]:
                print(av.get("avatar_id"), "|", av.get("avatar_name"), "|", av.get("gender"))
            return 0
        if a.list_voices:
            data = show(c.get("/v2/voices"))
            for v in (data.get("data") or {}).get("voices", []):
                if str(v.get("language", "")).lower().startswith("en"):
                    print(v.get("voice_id"), "|", v.get("name"), "|", v.get("gender"), "|", v.get("language"))
            return 0
        if not (a.avatar and a.voice):
            sys.exit("--avatar and --voice are required (discover ids with --list-avatars / --list-voices)")
        pkg = os.path.join(a.run_dir, "package")
        outdir = os.path.join(pkg, "videos")
        os.makedirs(outdir, exist_ok=True)
        log_path = os.path.join(outdir, "render_log.json")
        log = json.load(open(log_path)) if os.path.exists(log_path) else {}
        for pid in a.pieces.split(","):
            script = os.path.join(pkg, f"{pid}-video-script.md")
            sc = scenes(script)
            title = open(script, encoding="utf-8").readline().lstrip("# ").strip()
            if not sc:
                print(f"{pid}: no scenes parsed from {script}", file=sys.stderr)
                continue
            payload = {
                "title": title,
                "caption": False,
                "dimension": {"width": a.width, "height": a.height},
                "video_inputs": [{
                    "character": {"type": "avatar", "avatar_id": a.avatar, "avatar_style": "normal"},
                    "voice": {"type": "text", "voice_id": a.voice, "input_text": s["narration"], "speed": 1.0},
                    "background": {"type": "color", "value": a.background},
                } for s in sc],
            }
            data = show(c.post("/v2/video/generate", json=payload))
            vid = (data.get("data") or {}).get("video_id")
            print(f"{pid}: submitted {len(sc)} scenes, video_id={vid}")
            log[pid] = {"video_id": vid, "title": title, "scenes": len(sc), "status": "submitted"}
            json.dump(log, open(log_path, "w"), indent=2)
        for pid, entry in log.items():
            vid = entry.get("video_id")
            if not vid or entry.get("status") == "completed":
                continue
            while True:
                data = show(c.get("/v1/video_status.get", params={"video_id": vid}))
                st = (data.get("data") or {})
                status = st.get("status")
                if status == "completed":
                    url = st.get("video_url")
                    dest = os.path.join(outdir, f"{pid}.mp4")
                    with httpx.stream("GET", url, timeout=300, follow_redirects=True) as r, open(dest, "wb") as fh:
                        for chunk in r.iter_bytes(1 << 16):
                            fh.write(chunk)
                    entry.update({"status": "completed", "mp4": dest, "duration": st.get("duration")})
                    json.dump(log, open(log_path, "w"), indent=2)
                    print(f"{pid}: downloaded {dest}")
                    break
                if status == "failed":
                    entry.update({"status": "failed", "error": st.get("error")})
                    json.dump(log, open(log_path, "w"), indent=2)
                    print(f"{pid}: HeyGen reported failure: {st.get('error')}", file=sys.stderr)
                    break
                print(f"{pid}: {status}...", file=sys.stderr)
                time.sleep(20)
    return 0


if __name__ == "__main__":
    sys.exit(main())
