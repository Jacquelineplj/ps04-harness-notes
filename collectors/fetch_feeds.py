#!/usr/bin/env python3
"""Discover written items from configured RSS/Atom feeds.

Emits one candidate per entry: item_id "feed:<sha256(canonical url)[:16]>",
publication date from the feed, media_url null. Entries that carry an audio or
video enclosure are discovery routes to media, not written items, and are skipped
(counted in the receipt). When a feed ships the full article body, that HTML is
retained under data/media/feeds/ so extraction does not depend on re-scraping.
"""
from __future__ import annotations

import os
import sys

import feedparser

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from lib.receipt import Receipt  # noqa: E402
from lib.sources import (canonical_url, emit, fetch_bytes, load_sources, now_iso, older_than_lookback,  # noqa: E402
                         short_hash, simulated_failure, source_int, strip_html, struct_to_iso)

MEDIA_DIR = os.path.join(ROOT, "data", "media", "feeds")


def has_media_enclosure(entry) -> bool:
    for enc in entry.get("enclosures", []) or []:
        t = (enc.get("type") or "").lower()
        if t.startswith("audio/") or t.startswith("video/"):
            return True
    for link in entry.get("links", []) or []:
        if link.get("rel") == "enclosure" and (link.get("type") or "").lower().split("/")[0] in ("audio", "video"):
            return True
    return False


def full_content(entry) -> str | None:
    best = None
    for c in entry.get("content", []) or []:
        v = c.get("value") or ""
        if best is None or len(v) > len(best):
            best = v
    return best


def retain_content(item_hash16: str, html: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    rel = os.path.join("data", "media", "feeds", f"{item_hash16}-{short_hash(html, 12)}.html")
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
    return rel


def collect(src: dict, receipt: Receipt, counters: dict) -> int:
    url = src["url"]
    raw, final_url, status = fetch_bytes(url, timeout=90.0, accept="application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8")
    parsed = feedparser.parse(raw)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"feed could not be parsed: {getattr(parsed, 'bozo_exception', 'unknown error')}")
    max_items = source_int(src, "max_items", 8)
    lookback = source_int(src, "lookback_days", 60)
    entries = []
    for e in parsed.entries:
        published = struct_to_iso(e.get("published_parsed")) or struct_to_iso(e.get("updated_parsed"))
        entries.append((published, e))
    entries.sort(key=lambda t: (t[0] is None, t[0] or ""), reverse=False)
    entries.sort(key=lambda t: t[0] or "", reverse=True)
    emitted = 0
    for published, e in entries:
        if emitted >= max_items:
            break
        link = e.get("link")
        if not link:
            counters["skipped_no_link"] += 1
            continue
        if has_media_enclosure(e):
            counters["skipped_media_enclosure"] += 1
            continue
        if older_than_lookback(published, lookback):
            counters["skipped_beyond_lookback"] += 1
            continue
        curl = canonical_url(link)
        h16 = short_hash(curl)
        record = {
            "item_id": f"feed:{h16}",
            "source_id": src["source_id"],
            "publisher_id": src["publisher_id"],
            "kind": "feed",
            "title": strip_html(e.get("title") or "") or "(untitled)",
            "url": curl,
            "published_at": published,
            "retrieved_at": now_iso(),
            "media_url": None,
            "original_url": link,
            "summary": strip_html(e.get("summary") or "")[:400] or None,
            "authors": [a.get("name") for a in (e.get("authors") or []) if a.get("name")] or None,
            "feed_content_path": None,
            "source_perspective": src.get("perspective"),
        }
        body = full_content(e)
        if body and len(strip_html(body)) >= 1500:
            record["feed_content_path"] = retain_content(h16, body)
        emit(record)
        emitted += 1
    counters["entries_seen"] += len(parsed.entries)
    return emitted


def main(run_dir: str) -> int:
    receipt = Receipt(run_dir, "fetch_feeds", tools=["httpx", "feedparser"])
    try:
        sources = load_sources(run_dir, "feed")
    except (ValueError, OSError, KeyError) as exc:
        receipt.add_error(f"invalid sources.json: {exc}")
        receipt.finish("invalid_input", input_count=None, output_count=0, cost_usd=0.0, cost_is_estimate=False)
        print(f"fetch_feeds: invalid configuration: {exc}", file=sys.stderr)
        return 2
    if not sources:
        receipt.finish("completed", input_count=0, output_count=0, cost_usd=0.0, cost_is_estimate=False, unconfigured=True)
        print("fetch_feeds: no feed sources configured", file=sys.stderr)
        return 0
    counters = {"entries_seen": 0, "skipped_media_enclosure": 0, "skipped_beyond_lookback": 0, "skipped_no_link": 0}
    per_source = {}
    failed = 0
    total = 0
    sim_after = simulated_failure("feeds")
    for idx, src in enumerate(sources):
        if sim_after is not None and idx >= sim_after:
            receipt.add_error("simulated collector failure (SIMULATE_COLLECTOR_FAILURE=feeds); remaining sources not collected",
                              source_id=src["source_id"], simulated=True)
            failed += 1
            break
        try:
            n = collect(src, receipt, counters)
            per_source[src["source_id"]] = {"status": "ok", "candidates": n}
            total += n
            print(f"fetch_feeds: {src['source_id']}: {n} candidates", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - every source failure is recorded, not hidden
            failed += 1
            per_source[src["source_id"]] = {"status": "failed", "error": str(exc)[:300]}
            receipt.add_error(str(exc)[:500], source_id=src["source_id"], url=src["url"])
            print(f"fetch_feeds: {src['source_id']} FAILED: {exc}", file=sys.stderr)
    status = "completed" if failed == 0 else "completed_with_errors"
    receipt.finish(status, input_count=len(sources), output_count=total, cost_usd=0.0, cost_is_estimate=False,
                   sources=per_source, counters=counters, failed_sources=failed, simulated=sim_after is not None)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: fetch_feeds.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
