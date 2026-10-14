#!/usr/bin/env python3
"""Small shared plumbing for collectors: source snapshots, HTTP fetches, URL
canonicalisation, dates, hashing and the simulated-failure switch."""
from __future__ import annotations

import datetime as _dt
import hashlib
import html as _html
import json
import os
import re
import sys
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from dateutil import parser as dateparser

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 HarnessNotes-pipeline/1.0 (MIT 1.125 coursework)")
KINDS = ("feed", "youtube", "podcast")
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "fbclid",
                   "gclid", "mc_cid", "mc_eid", "ref", "ref_src", "source", "s", "si", "feature", "igshid", "_hsenc", "_hsmi"}


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_run(run_dir: str) -> dict:
    with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as fh:
        return json.load(fh)


def load_sources(run_dir: str, kind: str) -> list:
    """Read the run's snapshot of config/sources.json and return sources of `kind`.
    Raises ValueError for malformed definitions (callers exit 2)."""
    path = os.path.join(run_dir, "config", "sources.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("sources.json must be an array")
    out = []
    for i, src in enumerate(data):
        for k in ("source_id", "publisher_id", "kind", "url"):
            if not isinstance(src.get(k), str) or not src[k]:
                raise ValueError(f"sources[{i}] missing nonempty {k!r}")
        if src["kind"] not in KINDS:
            raise ValueError(f"sources[{i}] kind {src['kind']!r} not in {KINDS}")
        if src["kind"] == kind:
            out.append(src)
    return out


def source_int(src: dict, key: str, default: int) -> int:
    try:
        return int(src.get(key, default))
    except (TypeError, ValueError):
        return default


def fetch_bytes(url: str, timeout: float = 60.0, retries: int = 2, accept: str | None = None):
    """GET with a browser user agent; returns (bytes, final_url, status). Raises on failure."""
    headers = {"User-Agent": UA, "Accept": accept or "*/*", "Accept-Language": "en-US,en;q=0.8"}
    last = None
    for attempt in range(retries + 1):
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
                resp = client.get(url)
            if resp.status_code >= 400:
                raise httpx.HTTPStatusError(f"HTTP {resp.status_code} for {url}", request=resp.request, response=resp)
            return resp.content, str(resp.url), resp.status_code
        except (httpx.HTTPError, OSError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"fetch failed for {url}: {last}")


def download_file(url: str, dest: str, timeout: float = 120.0) -> int:
    """Stream a media file to disk; returns byte count. Partial files are removed on failure."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    n = 0
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": UA}) as client:
            with client.stream("GET", url) as resp:
                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code} for {url}")
                with open(tmp, "wb") as fh:
                    for chunk in resp.iter_bytes(1 << 16):
                        fh.write(chunk)
                        n += len(chunk)
        os.replace(tmp, dest)
        return n
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


_ARXIV = re.compile(r"^/(abs|pdf|html)/(\d{4}\.\d{4,5})(v\d+)?(\.pdf)?/?$")


def canonical_url(url: str) -> str:
    """Stable identity for written items: lowercase host, no fragment, no tracking
    params, no trailing slash, arXiv version suffixes stripped and /pdf -> /abs."""
    if not url:
        return url
    parts = urlsplit(url.strip())
    scheme = (parts.scheme or "https").lower()
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path or "/"
    if host == "arxiv.org":
        m = _ARXIV.match(path)
        if m:
            path = f"/abs/{m.group(2)}"
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")]
    if host in ("youtube.com", "m.youtube.com") and path == "/watch":
        query = [(k, v) for k, v in query if k == "v"]
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urlunsplit((scheme, host, path, urlencode(query), ""))


def short_hash(s: str, n: int = 16) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def struct_to_iso(st) -> str | None:
    """feedparser *_parsed struct_time (already UTC) -> ISO 8601 UTC string."""
    if not st:
        return None
    try:
        return _dt.datetime(*st[:6], tzinfo=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None


def parse_date_iso(value) -> str | None:
    """Parse an arbitrary date string to ISO UTC; None when absent or unparseable."""
    if not value or not isinstance(value, str):
        return None
    try:
        dt = dateparser.parse(value)
    except (ValueError, OverflowError, TypeError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch_to_iso(ts) -> str | None:
    try:
        return _dt.datetime.fromtimestamp(int(ts), tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def older_than_lookback(published_iso: str | None, lookback_days: int) -> bool:
    """True when the date is known and older than the collector's discovery horizon."""
    if not published_iso:
        return False
    try:
        d = _dt.datetime.strptime(published_iso, "%Y-%m-%dT%H:%M:%SZ").date()
    except ValueError:
        return False
    return d < (_dt.datetime.now(_dt.timezone.utc).date() - _dt.timedelta(days=lookback_days))


_TAG = re.compile(r"<[^>]+>")


def strip_html(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", _html.unescape(_TAG.sub(" ", s))).strip()


_YT_ID = re.compile(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|live/|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})")


def youtube_ids(text: str | None) -> list:
    return sorted(set(_YT_ID.findall(text or "")))


def simulated_failure(kind: str):
    """SIMULATE_COLLECTOR_FAILURE=podcasts[:after=N] makes that collector stop after N
    sources with a clearly labelled simulated error. Returns N or None."""
    spec = os.environ.get("SIMULATE_COLLECTOR_FAILURE", "").strip()
    if not spec:
        return None
    name, _, opts = spec.partition(":")
    if name.strip() != kind:
        return None
    after = 1
    for part in opts.split(","):
        if part.startswith("after="):
            try:
                after = int(part[6:])
            except ValueError:
                pass
    return after


def emit(record: dict):
    sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
    sys.stdout.flush()
