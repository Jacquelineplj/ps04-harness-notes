#!/usr/bin/env python3
"""Discover podcast episodes and their audio enclosures from configured feeds.

item_id is "podcast:<sha256(guid or enclosure url)[:16]>"; media_url is the audio
enclosure. Episode descriptions are scanned for YouTube links so extraction can
reconcile a podcast copy with the same recording on YouTube.
"""
from __future__ import annotations

import os
import re
import sys

import feedparser

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.receipt import Receipt  # noqa: E402
from lib.sources import (canonical_url, emit, fetch_bytes, load_sources, now_iso, older_than_lookback,  # noqa: E402
                         short_hash, simulated_failure, source_int, strip_html, struct_to_iso, youtube_ids)


def audio_enclosure(entry):
    for enc in entry.get("enclosures", []) or []:
        href = enc.get("href") or enc.get("url")
        t = (enc.get("type") or "").lower()
        if href and (t.startswith("audio/") or t == "" or href.lower().split("?")[0].endswith((".mp3", ".m4a", ".aac", ".ogg", ".wav"))):
            return href, t or None, enc.get("length")
    for link in entry.get("links", []) or []:
        if link.get("rel") == "enclosure" and (link.get("type") or "").startswith("audio/"):
            return link.get("href"), link.get("type"), link.get("length")
    return None, None, None


def duration_seconds(entry):
    raw = entry.get("itunes_duration")
    if not raw:
        return None
    raw = str(raw).strip()
    if re.fullmatch(r"\d+", raw):
        return int(raw)
    parts = raw.split(":")
    try:
        parts = [int(float(p)) for p in parts]
    except ValueError:
        return None
    secs = 0
    for p in parts:
        secs = secs * 60 + p
    return secs


def collect(src: dict, receipt: Receipt, counters: dict) -> int:
    raw, _, _ = fetch_bytes(src["url"], timeout=120.0, accept="application/rss+xml, application/xml;q=0.9, */*;q=0.8")
    parsed = feedparser.parse(raw)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"feed could not be parsed: {getattr(parsed, 'bozo_exception', 'unknown error')}")
    max_items = source_int(src, "max_items", 2)
    lookback = source_int(src, "lookback_days", 45)
    max_duration = source_int(src, "max_duration_seconds", 7200)
    # Optional discovery pre-filter: transcription is expensive, so a source may require a
    # keyword (regex) in the episode title or description. Skipped episodes are counted.
    include = re.compile(src["include_keywords"], re.I) if src.get("include_keywords") else None
    entries = []
    for e in parsed.entries:
        published = struct_to_iso(e.get("published_parsed")) or struct_to_iso(e.get("updated_parsed"))
        entries.append((published, e))
    entries.sort(key=lambda t: t[0] or "", reverse=True)
    counters["entries_seen"] += len(entries)
    emitted = 0
    for published, e in entries:
        if emitted >= max_items:
            break
        href, mime, length = audio_enclosure(e)
        if not href:
            counters["skipped_no_audio"] += 1
            continue
        if older_than_lookback(published, lookback):
            counters["skipped_beyond_lookback"] += 1
            continue
        dur = duration_seconds(e)
        if dur is not None and dur > max_duration:
            counters["skipped_too_long"] += 1
            continue
        guid = e.get("id") or href
        description = strip_html(e.get("summary") or "")
        if include and not include.search(strip_html(e.get("title") or "") + " " + description[:300]):
            counters["skipped_keyword_filter"] += 1
            continue
        content = ""
        for c in e.get("content", []) or []:
            content += " " + (c.get("value") or "")
        page = e.get("link") or href
        emit({
            "item_id": f"podcast:{short_hash(guid)}",
            "source_id": src["source_id"],
            "publisher_id": src["publisher_id"],
            "kind": "podcast",
            "title": strip_html(e.get("title") or "") or "(untitled)",
            "url": canonical_url(page) if page.startswith("http") else page,
            "published_at": published,
            "retrieved_at": now_iso(),
            "media_url": href,
            "episode_guid": guid,
            "enclosure_type": mime,
            "enclosure_length": int(length) if str(length or "").isdigit() else None,
            "duration_seconds": dur,
            "description": description[:600] or None,
            "description_youtube_ids": youtube_ids(description + " " + content + " " + (e.get("link") or "")),
            "source_perspective": src.get("perspective"),
        })
        emitted += 1
    return emitted


def main(run_dir: str) -> int:
    receipt = Receipt(run_dir, "fetch_podcasts", tools=["httpx", "feedparser"])
    try:
        sources = load_sources(run_dir, "podcast")
    except (ValueError, OSError, KeyError) as exc:
        receipt.add_error(f"invalid sources.json: {exc}")
        receipt.finish("invalid_input", output_count=0, cost_usd=0.0, cost_is_estimate=False)
        print(f"fetch_podcasts: invalid configuration: {exc}", file=sys.stderr)
        return 2
    if not sources:
        receipt.finish("completed", input_count=0, output_count=0, cost_usd=0.0, cost_is_estimate=False, unconfigured=True)
        print("fetch_podcasts: no podcast sources configured", file=sys.stderr)
        return 0
    counters = {"entries_seen": 0, "skipped_no_audio": 0, "skipped_beyond_lookback": 0, "skipped_too_long": 0, "skipped_keyword_filter": 0}
    per_source, failed, total = {}, 0, 0
    sim_after = simulated_failure("podcasts")
    for idx, src in enumerate(sources):
        if sim_after is not None and idx >= sim_after:
            receipt.add_error("simulated collector failure (SIMULATE_COLLECTOR_FAILURE=podcasts); remaining sources not collected",
                              source_id=src["source_id"], simulated=True)
            failed += 1
            break
        try:
            n = collect(src, receipt, counters)
            per_source[src["source_id"]] = {"status": "ok", "candidates": n}
            total += n
            print(f"fetch_podcasts: {src['source_id']}: {n} candidates", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            per_source[src["source_id"]] = {"status": "failed", "error": str(exc)[:300]}
            receipt.add_error(str(exc)[:500], source_id=src["source_id"], url=src["url"])
            print(f"fetch_podcasts: {src['source_id']} FAILED: {exc}", file=sys.stderr)
    receipt.finish("completed" if failed == 0 else "completed_with_errors", input_count=len(sources), output_count=total,
                   cost_usd=0.0, cost_is_estimate=False, sources=per_source, counters=counters, failed_sources=failed,
                   simulated=sim_after is not None)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: fetch_podcasts.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
