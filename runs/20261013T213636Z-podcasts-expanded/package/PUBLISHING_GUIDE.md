# Publishing guide for this package

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
