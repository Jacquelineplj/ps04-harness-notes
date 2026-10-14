#!/usr/bin/env python3
"""Turn candidates into evidence items with retained text and timestamped transcripts.

Per kind:
  feed     retained feed body (data/media/feeds) or fetched page -> trafilatura text;
           arXiv abstracts use the HTML rendering, falling back to the PDF (pymupdf).
  youtube  yt-dlp captions (manual "en", then original-language auto captions) as
           json3 -> ~30 s segments; if no captions, audio (m4a) -> faster-whisper.
  podcast  enclosure download -> faster-whisper (CPU, int8) -> segments.

Identity and versions:
  version_id = sha256 of compact sorted JSON {title, url, published_at, text, segments}
  assets     data/assets/<kind>/<sha256(item_id)[:16]>/<version_id[:12]>.txt (+ .segments.json)
             written once, never overwritten.
Reuse: the store is queried through `data/store.sh list`; media transcripts are
reused whenever the stored item has the same media/url and its assets exist, and
written items are reused in replay mode (EXTRACT_REFRESH=1 forces refetch).
Reconciliation: a podcast episode and its YouTube upload resolve to one item; the
dropped candidate is listed in RUN_DIR/duplicates.jsonl and as `aliases` on the keeper.

Environment: WHISPER_MODEL (small), MAX_TRANSCRIBE_SECONDS (3600), RETAIN_MEDIA (1),
CAPTION_SLEEP_SECONDS (2), EXTRACT_REFRESH (unset).
"""
from __future__ import annotations

import datetime as _dt
import difflib
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.evidence import compute_version_id, load_segments, load_text, normalize_text  # noqa: E402
from lib.receipt import Receipt  # noqa: E402
from lib.sources import download_file, fetch_bytes, load_run, short_hash  # noqa: E402

ASSETS_DIR = "data/assets"
MEDIA_DIR = "data/media"
MIN_TEXT_CHARS = 800
THIN_TEXT_CHARS = 2000
RETAIN_MEDIA = os.environ.get("RETAIN_MEDIA", "1") != "0"
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
MAX_TRANSCRIBE_SECONDS = int(os.environ.get("MAX_TRANSCRIBE_SECONDS", "3600"))
CAPTION_SLEEP = float(os.environ.get("CAPTION_SLEEP_SECONDS", "2"))
EXTRACT_REFRESH = os.environ.get("EXTRACT_REFRESH") == "1"
SEGMENT_TARGET_SECONDS = 30.0
SEGMENT_MAX_WORDS = 90
BULKY_FIELDS = ("caption_tracks",)
ORDER = {"feed": 0, "youtube": 1, "podcast": 2}


class Unprocessable(Exception):
    pass


def log(msg: str):
    print(f"extract_content: {msg}", file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------- store access (through the interface)

def store_index() -> dict:
    proc = subprocess.run(["bash", os.path.join("data", "store.sh"), "list"], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        log(f"store list unavailable ({proc.stderr.strip()[:200]}); nothing will be reused")
        return {}
    idx = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            rec = json.loads(line)
            idx[rec["item_id"]] = rec
    return idx


# ----------------------------------------------------------------------------- assets

def asset_base(kind: str, item_id: str, version_id: str) -> str:
    return os.path.join(ASSETS_DIR, kind, short_hash(item_id), version_id[:12])


def write_once(rel_path: str, content: str):
    path = os.path.join(ROOT, rel_path)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            if fh.read() == content:
                return
        raise RuntimeError(f"asset collision: {rel_path} exists with different content")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def segments_json(segments: list) -> str:
    return json.dumps(segments, indent=2, ensure_ascii=False) + "\n"


# ----------------------------------------------------------------------------- segments

def merge_segments(raw: list, target_seconds: float = SEGMENT_TARGET_SECONDS, max_words: int = SEGMENT_MAX_WORDS) -> list:
    """raw: [(start, end, text)] in order -> ~30 s chunks with ids s-0001..."""
    out, cur_start, cur_end, cur_text, cur_words = [], None, None, [], 0
    for start, end, text in raw:
        text = re.sub(r"\s+", " ", text or "").strip()
        if not text:
            continue
        words = len(text.split())
        if cur_start is not None and ((end - cur_start) > target_seconds or cur_words + words > max_words):
            out.append((cur_start, cur_end, " ".join(cur_text)))
            cur_start, cur_end, cur_text, cur_words = None, None, [], 0
        if cur_start is None:
            cur_start = start
        cur_end = max(end, cur_end or 0)
        cur_text.append(text)
        cur_words += words
    if cur_text:
        out.append((cur_start, cur_end, " ".join(cur_text)))
    return [{"segment_id": f"s-{i:04d}", "start_seconds": round(float(s), 2), "end_seconds": round(float(e), 2), "text": t}
            for i, (s, e, t) in enumerate(out, 1)]


def segments_from_json3(data: dict) -> list:
    raw = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        text = "".join(s.get("utf8", "") for s in segs)
        if not text.strip():
            continue
        start = (ev.get("tStartMs") or 0) / 1000.0
        end = start + (ev.get("dDurationMs") or 0) / 1000.0
        raw.append((start, end, text.replace("\n", " ")))
    return merge_segments(raw)


def text_from_segments(segments: list) -> str:
    return "\n".join(s["text"] for s in segments) + "\n"


# ----------------------------------------------------------------------------- transcription

_WHISPER = None


def whisper():
    global _WHISPER
    if _WHISPER is None:
        from faster_whisper import WhisperModel
        log(f"loading faster-whisper model {WHISPER_MODEL} (cpu/int8)")
        _WHISPER = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8", cpu_threads=min(8, os.cpu_count() or 4))
    return _WHISPER


def media_duration(path: str):
    try:
        import av
        with av.open(path) as container:
            if container.duration:
                return container.duration / av.time_base
    except Exception:  # noqa: BLE001
        return None
    return None


def transcribe(path: str) -> tuple:
    duration = media_duration(path)
    kwargs = dict(beam_size=1, vad_filter=True, condition_on_previous_text=False)
    truncated_at = None
    if duration and duration > MAX_TRANSCRIBE_SECONDS:
        kwargs["clip_timestamps"] = [0, MAX_TRANSCRIBE_SECONDS]
        truncated_at = MAX_TRANSCRIBE_SECONDS
    t0 = time.time()
    segs, info = whisper().transcribe(path, **kwargs)
    raw = [(s.start, s.end, s.text) for s in segs]
    elapsed = time.time() - t0
    segments = merge_segments(raw)
    meta = {"language": getattr(info, "language", None), "duration_seconds": duration,
            "transcribed_seconds": (truncated_at or duration), "truncated_at_seconds": truncated_at,
            "whisper_model": WHISPER_MODEL, "wall_seconds": round(elapsed, 1)}
    return segments, meta


# ----------------------------------------------------------------------------- written items

def arxiv_id(url: str):
    m = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", url)
    return m.group(1) if m else None


def extract_written(cand: dict) -> tuple:
    import trafilatura
    url = cand["url"]
    html, text, method = None, None, None
    fcp = cand.get("feed_content_path")
    if fcp and os.path.exists(os.path.join(ROOT, fcp)):
        with open(os.path.join(ROOT, fcp), encoding="utf-8") as fh:
            html = fh.read()
        method = "feed_content"
    aid = arxiv_id(url)
    if html is None and aid:
        try:
            raw, _, _ = fetch_bytes(f"https://arxiv.org/html/{aid}", timeout=90.0)
            html, method = raw.decode("utf-8", "replace"), "arxiv_html"
        except Exception as exc:  # noqa: BLE001
            log(f"{cand['item_id']}: arXiv HTML unavailable ({str(exc)[:80]}); trying PDF")
            raw, _, _ = fetch_bytes(f"https://arxiv.org/pdf/{aid}", timeout=120.0)
            import pymupdf
            doc = pymupdf.open(stream=raw, filetype="pdf")
            pages = [page.get_text() for page in doc][:40]
            text, method = "\n".join(pages), "arxiv_pdf"
    if html is None and text is None:
        raw, _, _ = fetch_bytes(url, timeout=90.0, accept="text/html,application/xhtml+xml,*/*;q=0.8")
        html, method = raw.decode("utf-8", "replace"), "html"
    if text is None:
        text = trafilatura.extract(html, url=url, include_comments=False, include_tables=True,
                                   favor_recall=True, deduplicate=True) or ""
    if method in ("arxiv_html", "arxiv_pdf"):
        cut = text.rfind("\nReferences\n")
        if cut > len(text) * 0.5:
            text = text[:cut]
    text = normalize_text(text)
    if len(text) < MIN_TEXT_CHARS:
        raise Unprocessable(f"insufficient_text: {len(text)} chars via {method}")
    return text, method


# ----------------------------------------------------------------------------- youtube


class _StderrLogger:
    """Route every yt-dlp message to stderr so stdout stays pure JSONL."""

    def debug(self, msg):
        if msg.startswith("[debug]"):
            return
        print(msg, file=sys.stderr)

    def info(self, msg):
        print(msg, file=sys.stderr)

    def warning(self, msg):
        print(msg, file=sys.stderr)

    def error(self, msg):
        print(msg, file=sys.stderr)


def ydl_base():
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "logger": _StderrLogger(),
            "socket_timeout": 60, "retries": 3}
    if shutil.which("node"):
        opts["js_runtimes"] = {"node": {}}
    return opts


def youtube_captions(video_id: str, cand: dict) -> tuple:
    import yt_dlp
    outdir = os.path.join(ROOT, MEDIA_DIR, "youtube", video_id)
    os.makedirs(outdir, exist_ok=True)
    tracks = cand.get("caption_tracks") or {}
    attempts = []
    if "en" in (tracks.get("manual_en") or []):
        attempts.append(("manual", ["en"]))
    attempts += [("auto", ["en-orig"]), ("auto", ["en"])]
    url = f"https://www.youtube.com/watch?v={video_id}"
    for kind, langs in attempts:
        existing = glob.glob(os.path.join(outdir, f"{video_id}.{langs[0]}.json3"))
        if not existing:
            opts = ydl_base()
            opts.update({"skip_download": True, "writesubtitles": kind == "manual", "writeautomaticsub": kind == "auto",
                         "subtitleslangs": langs, "subtitlesformat": "json3",
                         "outtmpl": os.path.join(outdir, "%(id)s.%(ext)s")})
            try:
                with yt_dlp.YoutubeDL(opts) as y:
                    y.download([url])
            except Exception as exc:  # noqa: BLE001
                log(f"{video_id}: {kind} captions {langs} failed: {str(exc)[:120]}")
            finally:
                time.sleep(CAPTION_SLEEP)
            existing = glob.glob(os.path.join(outdir, f"{video_id}.{langs[0]}.json3"))
        if existing:
            with open(existing[0], encoding="utf-8") as fh:
                data = json.load(fh)
            segments = segments_from_json3(data)
            if segments:
                return segments, f"youtube_captions_{kind}", {"caption_file": os.path.relpath(existing[0], ROOT)}
    return [], None, {}


def youtube_audio(video_id: str) -> str:
    import yt_dlp
    outdir = os.path.join(ROOT, MEDIA_DIR, "youtube", video_id)
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, f"{video_id}.audio.*")):
        return f
    opts = ydl_base()
    opts.update({"format": "bestaudio[ext=m4a][protocol^=http]/bestaudio[protocol^=http]/bestaudio",
                 "outtmpl": os.path.join(outdir, "%(id)s.audio.%(ext)s"), "noplaylist": True})
    with yt_dlp.YoutubeDL(opts) as y:
        y.download([f"https://www.youtube.com/watch?v={video_id}"])
    files = glob.glob(os.path.join(outdir, f"{video_id}.audio.*"))
    if not files:
        raise Unprocessable("audio download produced no file")
    return files[0]


def extract_youtube(cand: dict, counters: dict) -> tuple:
    video_id = cand["item_id"].split(":", 1)[1]
    segments, source, meta = youtube_captions(video_id, cand)
    if segments:
        counters["caption_items"] += 1
        return segments, source, meta
    log(f"{cand['item_id']}: no captions; downloading audio for transcription")
    audio = youtube_audio(video_id)
    segments, meta = transcribe(audio)
    counters["whisper_items"] += 1
    counters["transcribed_seconds"] += float(meta.get("transcribed_seconds") or 0)
    meta["media_path"] = os.path.relpath(audio, ROOT)
    if not RETAIN_MEDIA:
        os.remove(audio)
        meta["media_retained"] = False
    if not segments:
        raise Unprocessable("transcription produced no speech segments")
    return segments, f"whisper:{WHISPER_MODEL}", meta


# ----------------------------------------------------------------------------- podcast

def extract_podcast(cand: dict, counters: dict) -> tuple:
    media_url = cand.get("media_url")
    if not media_url:
        raise Unprocessable("no media_url for podcast episode")
    ext = os.path.splitext(media_url.split("?")[0])[1].lower() or ".mp3"
    if ext not in (".mp3", ".m4a", ".aac", ".ogg", ".wav", ".mp4"):
        ext = ".mp3"
    dest = os.path.join(ROOT, MEDIA_DIR, "podcasts", f"{short_hash(cand['item_id'])}{ext}")
    if not os.path.exists(dest):
        log(f"{cand['item_id']}: downloading audio")
        download_file(media_url, dest, timeout=180.0)
        counters["media_downloaded"] += 1
    segments, meta = transcribe(dest)
    counters["whisper_items"] += 1
    counters["transcribed_seconds"] += float(meta.get("transcribed_seconds") or 0)
    meta["media_path"] = os.path.relpath(dest, ROOT)
    if not RETAIN_MEDIA:
        os.remove(dest)
        meta["media_retained"] = False
    if not segments:
        raise Unprocessable("transcription produced no speech segments")
    return segments, f"whisper:{WHISPER_MODEL}", meta


# ----------------------------------------------------------------------------- reuse

def reuse_prior(cand: dict, prior: dict | None, mode: str):
    """Return (text, segments, source, note) from stored assets when the material is unchanged, else None."""
    if not prior:
        return None
    kind = cand["kind"]
    if kind == "feed":
        if mode != "replay" or EXTRACT_REFRESH:
            return None
    else:
        same_media = (prior.get("media_url") == cand.get("media_url")) if kind == "podcast" else (prior.get("url") == cand.get("url"))
        if not same_media:
            return None
        cut = prior.get("transcript_truncated_at_seconds")
        if cut and cut < MAX_TRANSCRIBE_SECONDS and not EXTRACT_REFRESH == "never":
            return None  # the stored transcript was capped shorter than allowed now: transcribe again
    text = load_text(prior)
    if not text:
        return None
    segments = load_segments(prior) if kind != "feed" else None
    if kind != "feed" and not segments:
        return None
    return text, segments, prior.get("transcript_source") or "stored", "reused stored extraction"


# ----------------------------------------------------------------------------- reconciliation of recordings

def _norm_title(t: str) -> str:
    t = re.sub(r"^(ep(isode)?\.?\s*\d+[:.\-\s]+)", "", (t or "").lower())
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def _days_apart(a, b):
    try:
        da = _dt.datetime.strptime(a, "%Y-%m-%dT%H:%M:%SZ")
        db = _dt.datetime.strptime(b, "%Y-%m-%dT%H:%M:%SZ")
        return abs((da - db).days)
    except (TypeError, ValueError):
        return 999


def _same_recording(pod: dict, yt: dict):
    yt_id = yt["item_id"].split(":", 1)[1]
    if yt_id in (pod.get("description_youtube_ids") or []):
        return "podcast description links to the YouTube video"
    if pod.get("publisher_id") == yt.get("publisher_id"):
        sim = difflib.SequenceMatcher(None, _norm_title(pod.get("title")), _norm_title(yt.get("title"))).ratio()
        if sim >= 0.85 and _days_apart(pod.get("published_at"), yt.get("published_at")) <= 3:
            return f"same publisher, title similarity {sim:.2f}, published within 3 days"
    return None


def reconcile(cands: list, index: dict):
    """Returns (kept candidates, duplicate records)."""
    podcasts = [c for c in cands if c["kind"] == "podcast"]
    videos = [c for c in cands if c["kind"] == "youtube"]
    stored_pods = [r for r in index.values() if r.get("kind") == "podcast"]
    stored_vids = [r for r in index.values() if r.get("kind") == "youtube"]
    dropped, dups, aliases = set(), [], {}

    def drop(loser, keeper, basis):
        if loser["item_id"] in dropped:
            return
        dropped.add(loser["item_id"])
        dups.append({"item_id": loser["item_id"], "kind": loser["kind"], "url": loser.get("url"),
                     "duplicate_of": keeper["item_id"], "basis": basis})
        aliases.setdefault(keeper["item_id"], []).append(
            {"item_id": loser["item_id"], "kind": loser["kind"], "url": loser.get("url"),
             "media_url": loser.get("media_url"), "basis": basis})

    for pod in podcasts:
        for yt in videos:
            basis = _same_recording(pod, yt)
            if not basis:
                continue
            if yt["item_id"] in index and pod["item_id"] not in index:
                drop(pod, yt, basis)
            else:
                drop(yt, pod, basis)
    for yt in videos:
        if yt["item_id"] in dropped or yt["item_id"] in index:
            continue
        for sp in stored_pods:
            basis = _same_recording(sp, yt)
            if basis:
                drop(yt, sp, basis + " (stored item)")
                break
    for pod in podcasts:
        if pod["item_id"] in dropped or pod["item_id"] in index:
            continue
        for sv in stored_vids:
            basis = _same_recording(pod, sv)
            if basis:
                drop(pod, sv, basis + " (stored item)")
                break
    kept = []
    for c in cands:
        if c["item_id"] in dropped:
            continue
        if c["item_id"] in aliases:
            c = dict(c)
            c["aliases"] = (c.get("aliases") or []) + aliases[c["item_id"]]
        kept.append(c)
    return kept, dups


# ----------------------------------------------------------------------------- main

def main(run_dir: str) -> int:
    run = load_run(run_dir)
    mode = run.get("mode", "live")
    receipt = Receipt(run_dir, "extract_content", tools=["httpx", "trafilatura", "yt-dlp", f"faster-whisper ({WHISPER_MODEL})", "pymupdf"])
    counters = {"reused": 0, "fetched": 0, "caption_items": 0, "whisper_items": 0, "media_downloaded": 0,
                "transcribed_seconds": 0.0, "unprocessable": 0, "failed": 0, "thin": 0, "malformed_lines": 0, "duplicates": 0}
    cands = []
    seen = set()
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            for k in ("item_id", "kind", "title", "url"):
                if not rec.get(k):
                    raise ValueError(f"missing {k}")
            if rec["kind"] not in ORDER:
                raise ValueError(f"bad kind {rec['kind']!r}")
        except (json.JSONDecodeError, ValueError, AttributeError) as exc:
            counters["malformed_lines"] += 1
            receipt.add_error(f"line {n}: malformed candidate ({exc})")
            continue
        if rec["item_id"] in seen:  # same item discovered twice in one run (e.g. two feeds)
            continue
        seen.add(rec["item_id"])
        cands.append(rec)
    index = store_index()
    cands, dups = reconcile(cands, index)
    counters["duplicates"] = len(dups)
    with open(os.path.join(run_dir, "duplicates.jsonl"), "w", encoding="utf-8") as fh:
        for d in dups:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    cands.sort(key=lambda c: ORDER[c["kind"]])  # cheap written items first, transcription last
    emitted = 0
    for cand in cands:
        item_id, kind = cand["item_id"], cand["kind"]
        prior = index.get(item_id)
        try:
            reuse = reuse_prior(cand, prior, mode)
            meta = {}
            if reuse:
                text, segments, source, _ = reuse
                counters["reused"] += 1
                reused = True
            else:
                reused = False
                counters["fetched"] += 1
                if kind == "feed":
                    text, source = extract_written(cand)
                    segments = None
                elif kind == "youtube":
                    segments, source, meta = extract_youtube(cand, counters)
                    text = text_from_segments(segments)
                else:
                    segments, source, meta = extract_podcast(cand, counters)
                    text = text_from_segments(segments)
            version_id = compute_version_id(cand["title"], cand["url"], cand.get("published_at"), text, segments)
            base = asset_base(kind, item_id, version_id)
            text_path = base + ".txt"
            write_once(text_path, text)
            segments_path = None
            if segments is not None:
                segments_path = base + ".segments.json"
                write_once(segments_path, segments_json(segments))
            item = {k: v for k, v in cand.items() if k not in BULKY_FIELDS}
            item.update({
                "version_id": version_id,
                "text_path": text_path,
                "segments_path": segments_path,
                "transcript_source": source,
                "reused": reused,
                "text_chars": len(text),
                "word_count": len(text.split()),
                "segment_count": len(segments) if segments else 0,
                "media_path": meta.get("media_path") or (prior or {}).get("media_path"),
                "media_retained": meta.get("media_retained", (prior or {}).get("media_retained", RETAIN_MEDIA if kind != "feed" else None)),
                "transcript_truncated_at_seconds": meta.get("truncated_at_seconds") or (prior or {}).get("transcript_truncated_at_seconds"),
                "extracted_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
            if len(text) < THIN_TEXT_CHARS:
                item["thin"] = True
                counters["thin"] += 1
            sys.stdout.write(json.dumps(item, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            emitted += 1
            log(f"{item_id}: {source} ({len(text)} chars{', reused' if reused else ''})")
        except Unprocessable as exc:
            counters["unprocessable"] += 1
            receipt.add_error(f"unprocessable: {exc}", item_id=item_id, url=cand.get("url"))
            log(f"{item_id}: unprocessable: {exc}")
        except Exception as exc:  # noqa: BLE001 - recorded per item, pipeline continues
            counters["failed"] += 1
            receipt.add_error(f"{type(exc).__name__}: {str(exc)[:300]}", item_id=item_id, url=cand.get("url"))
            log(f"{item_id}: FAILED {type(exc).__name__}: {str(exc)[:200]}")
    n_in = len(cands) + len(dups)
    if counters["malformed_lines"]:
        status, rc = "invalid_input", 2
    elif n_in and emitted == 0:
        status, rc = "failed", 1
    elif receipt.errors:
        status, rc = "completed_with_errors", 0
    else:
        status, rc = "completed", 0
    receipt.finish(status, input_count=n_in, output_count=emitted, cost_usd=0.0, cost_is_estimate=False,
                   counters=counters, mode=mode, retain_media=RETAIN_MEDIA, whisper_model=WHISPER_MODEL,
                   max_transcribe_seconds=MAX_TRANSCRIBE_SECONDS, cost_basis="local compute only")
    log(f"done: {emitted}/{n_in} items ({counters})")
    return rc


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: extract_content.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
