#!/usr/bin/env python3
"""Discover configured YouTube material (channels, playlists or single videos).

Uses yt-dlp metadata only (no media download here). item_id is the native video
id ("youtube:<id>"); published_at comes from the video's timestamp (upload or
scheduled release), falling back to the date-only upload_date (marked
published_precision "date"). Shorts (< 120 s) and live/upcoming streams are skipped.
"""
from __future__ import annotations

import os
import shutil
import sys
import time

import yt_dlp

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.receipt import Receipt  # noqa: E402
from lib.sources import emit, epoch_to_iso, load_sources, now_iso, older_than_lookback, simulated_failure, source_int  # noqa: E402

MIN_DURATION = 120


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



def ydl_opts(**extra):
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "logger": _StderrLogger(),
            "skip_download": True, "noplaylist": False, "socket_timeout": 60, "retries": 3}
    if shutil.which("node"):
        opts["js_runtimes"] = {"node": {}}
    opts.update(extra)
    return opts


def is_single_video(url: str) -> bool:
    return "watch?v=" in url or "youtu.be/" in url


def list_entries(url: str, limit: int) -> list:
    if is_single_video(url):
        return [{"url": url}]
    with yt_dlp.YoutubeDL(ydl_opts(extract_flat=True, playlistend=limit)) as y:
        info = y.extract_info(url, download=False)
    entries = info.get("entries") or []
    out = []
    for e in entries:
        if not e:
            continue
        if e.get("_type") == "playlist":  # a channel root lists tabs; descend into the uploads tab
            for sub in e.get("entries") or []:
                if sub:
                    out.append(sub)
        else:
            out.append(e)
    return out


def video_metadata(video_url: str) -> dict:
    with yt_dlp.YoutubeDL(ydl_opts()) as y:
        return y.extract_info(video_url, download=False)


def published_fields(v: dict):
    ts = v.get("release_timestamp") or v.get("timestamp")
    if ts:
        return epoch_to_iso(ts), "second"
    ud = v.get("upload_date")
    if ud and len(ud) == 8:
        return f"{ud[:4]}-{ud[4:6]}-{ud[6:]}T00:00:00Z", "date"
    return None, None


def collect(src: dict, receipt: Receipt, counters: dict) -> int:
    max_items = source_int(src, "max_items", 4)
    lookback = source_int(src, "lookback_days", 45)
    entries = list_entries(src["url"], limit=max(max_items * 3, 6))
    counters["entries_seen"] += len(entries)
    emitted = 0
    for e in entries:
        if emitted >= max_items:
            break
        vid = e.get("id")
        if e.get("duration") is not None and e["duration"] < MIN_DURATION:
            counters["skipped_short"] += 1
            continue
        if e.get("live_status") in ("is_live", "is_upcoming"):
            counters["skipped_live"] += 1
            continue
        video_url = f"https://www.youtube.com/watch?v={vid}" if vid else e.get("url")
        try:
            v = video_metadata(video_url)
        except Exception as exc:  # noqa: BLE001
            counters["metadata_failures"] += 1
            receipt.add_error(f"metadata failed: {str(exc)[:200]}", source_id=src["source_id"], url=video_url)
            continue
        time.sleep(1.0)
        vid = v.get("id") or vid
        duration = v.get("duration")
        if duration is not None and duration < MIN_DURATION:
            counters["skipped_short"] += 1
            continue
        if v.get("live_status") in ("is_live", "is_upcoming"):
            counters["skipped_live"] += 1
            continue
        published, precision = published_fields(v)
        if older_than_lookback(published, lookback):
            counters["skipped_beyond_lookback"] += 1
            continue
        subs = v.get("subtitles") or {}
        auto = v.get("automatic_captions") or {}
        emit({
            "item_id": f"youtube:{vid}",
            "source_id": src["source_id"],
            "publisher_id": src["publisher_id"],
            "kind": "youtube",
            "title": v.get("title") or "(untitled)",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "published_at": published,
            "retrieved_at": now_iso(),
            "media_url": None,
            "published_precision": precision,
            "duration_seconds": duration,
            "channel": v.get("channel") or v.get("uploader"),
            "channel_id": v.get("channel_id"),
            "description": (v.get("description") or "")[:600] or None,
            "caption_tracks": {"manual_en": [k for k in subs if k.startswith("en")],
                               "auto_en": [k for k in auto if k.startswith("en")]},
            "source_perspective": src.get("perspective"),
        })
        emitted += 1
    return emitted


def main(run_dir: str) -> int:
    receipt = Receipt(run_dir, "fetch_youtube", tools=[f"yt-dlp {yt_dlp.version.__version__}"])
    try:
        sources = load_sources(run_dir, "youtube")
    except (ValueError, OSError, KeyError) as exc:
        receipt.add_error(f"invalid sources.json: {exc}")
        receipt.finish("invalid_input", output_count=0, cost_usd=0.0, cost_is_estimate=False)
        print(f"fetch_youtube: invalid configuration: {exc}", file=sys.stderr)
        return 2
    if not sources:
        receipt.finish("completed", input_count=0, output_count=0, cost_usd=0.0, cost_is_estimate=False, unconfigured=True)
        print("fetch_youtube: no youtube sources configured", file=sys.stderr)
        return 0
    counters = {"entries_seen": 0, "skipped_short": 0, "skipped_live": 0, "skipped_beyond_lookback": 0, "metadata_failures": 0}
    per_source, failed, total = {}, 0, 0
    sim_after = simulated_failure("youtube")
    for idx, src in enumerate(sources):
        if sim_after is not None and idx >= sim_after:
            receipt.add_error("simulated collector failure (SIMULATE_COLLECTOR_FAILURE=youtube); remaining sources not collected",
                              source_id=src["source_id"], simulated=True)
            failed += 1
            break
        try:
            n = collect(src, receipt, counters)
            per_source[src["source_id"]] = {"status": "ok", "candidates": n}
            total += n
            print(f"fetch_youtube: {src['source_id']}: {n} candidates", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            per_source[src["source_id"]] = {"status": "failed", "error": str(exc)[:300]}
            receipt.add_error(str(exc)[:500], source_id=src["source_id"], url=src["url"])
            print(f"fetch_youtube: {src['source_id']} FAILED: {exc}", file=sys.stderr)
    receipt.finish("completed" if failed == 0 else "completed_with_errors", input_count=len(sources), output_count=total,
                   cost_usd=0.0, cost_is_estimate=False, sources=per_source, counters=counters, failed_sources=failed,
                   simulated=sim_after is not None)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: fetch_youtube.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
