#!/usr/bin/env python3
"""Helpers for reading retained evidence assets and resolving locators.

Any stage may read retained text/transcript assets referenced by item records
(the evidence *index* itself is only touched by data/store.sh). Paths in records
are repository-relative, so everything resolves from PIPELINE_ROOT.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata

ROOT = os.environ.get("PIPELINE_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def abs_path(rel: str | None) -> str | None:
    if not rel:
        return None
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def read_jsonl(path: str) -> list:
    out = []
    with open(abs_path(path), encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def load_text(item: dict) -> str:
    p = abs_path(item.get("text_path"))
    if not p or not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def load_segments(item: dict) -> list:
    p = abs_path(item.get("segments_path"))
    if not p or not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else []


def segment_by_id(segments: list, segment_id: str) -> dict | None:
    for s in segments:
        if s.get("segment_id") == segment_id:
            return s
    return None


_WS = re.compile(r"\s+")
_QUOTE_MAP = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "−": "-", " ": " ", "…": "...",
})


def normalize_ws(s: str) -> str:
    return _WS.sub(" ", (s or "")).strip()


def normalize_loose(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").translate(_QUOTE_MAP)
    return normalize_ws(s).lower()


def find_quote(text: str, quote: str) -> dict:
    """Locate `quote` inside `text`.

    Returns {"found": bool, "exact": str|None, "mode": "exact"|"loose"|None}.
    `exact` is the verbatim span from `text` (whitespace-normalised) so callers
    can canonicalise a loosely matching quote to the retained wording.
    """
    if not text or not quote:
        return {"found": False, "exact": None, "mode": None}
    norm_text = normalize_ws(text)
    norm_quote = normalize_ws(quote)
    if norm_quote and norm_quote in norm_text:
        return {"found": True, "exact": norm_quote, "mode": "exact"}
    loose_text = normalize_loose(norm_text)
    loose_quote = normalize_loose(norm_quote)
    if not loose_quote:
        return {"found": False, "exact": None, "mode": None}
    idx = loose_text.find(loose_quote)
    if idx < 0:
        return {"found": False, "exact": None, "mode": None}
    # Map the loose match back to the normalised original text. NFKC + the
    # quote map keep character counts identical except for the ellipsis, so
    # fall back to a tolerant window when lengths drift.
    span = norm_text[idx: idx + len(loose_quote)]
    if normalize_loose(span) == loose_quote:
        return {"found": True, "exact": span, "mode": "loose"}
    for extra in range(1, 6):
        span = norm_text[idx: idx + len(loose_quote) + extra]
        if normalize_loose(span) == loose_quote:
            return {"found": True, "exact": span, "mode": "loose"}
    return {"found": True, "exact": None, "mode": "loose"}


def fmt_timestamp(seconds) -> str:
    try:
        s = int(round(float(seconds)))
    except (TypeError, ValueError):
        return "?"
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def media_link(item: dict, start_seconds=None) -> str:
    """Audience-facing link to the passage: YouTube gets &t=, others keep the URL."""
    url = item.get("url") or item.get("media_url") or ""
    if start_seconds is None:
        return url
    try:
        t = int(float(start_seconds))
    except (TypeError, ValueError):
        return url
    if item.get("kind") == "youtube" and "youtube.com/watch" in url:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}t={t}s"
    if item.get("kind") == "youtube" and "youtu.be/" in url:
        return f"{url}?t={t}"
    return url


def resolve_evidence(ref: dict, item: dict) -> dict:
    """Check one evidence reference against the retained assets of `item`.

    Returns {"ok": bool, "problem": str|None, "passage": str|None,
             "start_seconds": float|None, "end_seconds": float|None, "exact": str|None}
    """
    loc = ref.get("locator") or {}
    ltype = loc.get("type")
    if ltype == "text":
        text = load_text(item)
        if not text:
            return {"ok": False, "problem": "retained text missing", "passage": None,
                    "start_seconds": None, "end_seconds": None, "exact": None}
        hit = find_quote(text, loc.get("quote") or "")
        if not hit["found"]:
            return {"ok": False, "problem": "quote not found in retained text", "passage": None,
                    "start_seconds": None, "end_seconds": None, "exact": None}
        return {"ok": True, "problem": None, "passage": hit["exact"] or normalize_ws(loc.get("quote")),
                "start_seconds": None, "end_seconds": None, "exact": hit["exact"], "mode": hit["mode"]}
    if ltype == "segment":
        segs = load_segments(item)
        if not segs:
            return {"ok": False, "problem": "segments file missing or empty", "passage": None,
                    "start_seconds": None, "end_seconds": None, "exact": None}
        seg = segment_by_id(segs, loc.get("segment_id"))
        if not seg:
            return {"ok": False, "problem": f"segment_id {loc.get('segment_id')!r} not found", "passage": None,
                    "start_seconds": None, "end_seconds": None, "exact": None}
        return {"ok": True, "problem": None, "passage": seg.get("text"),
                "start_seconds": seg.get("start_seconds"), "end_seconds": seg.get("end_seconds"), "exact": None}
    return {"ok": False, "problem": f"unknown locator type {ltype!r}", "passage": None,
            "start_seconds": None, "end_seconds": None, "exact": None}


# ----------------------------------------------------------------------------- shared by extraction + checks

_BOILERPLATE = re.compile(
    r"^(subscribe( now)?|share( this( post)?)?|leave a comment|sign in|sign up|log in|read more|"
    r"share this|copy link|facebook|email|notes|more|discussion about this post|"
    r"thanks for reading[^.]*\.?|ready for more\??|no posts|previous|next)\s*$", re.I)


def normalize_text(s: str) -> str:
    """Canonical form of retained text: LF newlines, no trailing spaces, at most one
    blank line in a row, short boilerplate lines removed, single trailing newline.
    The version hash is computed over exactly this string."""
    s = (s or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in s.split("\n"):
        line = line.rstrip()
        if len(line) < 60 and _BOILERPLATE.match(line.strip()):
            continue
        lines.append(line)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out + "\n" if out else ""


def compute_version_id(title: str, url: str, published_at, text: str, segments) -> str:
    """sha256 of compact, key-sorted JSON of the evidence-relevant fields.
    Written items pass segments=None; media items pass the segment list.
    Retrieval timestamps are deliberately excluded (verified against examples/)."""
    import hashlib
    payload = {"title": title, "url": url, "published_at": published_at, "text": text, "segments": segments}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- rendering for prompts

def item_header(item: dict, source_meta: dict | None = None) -> str:
    bits = [
        f"item_id: {item.get('item_id')}",
        f"version_id: {item.get('version_id')}",
        f"kind: {item.get('kind')}",
        f"publisher_id: {item.get('publisher_id')} (source_id: {item.get('source_id')})",
        f"published_at: {item.get('published_at')}",
        f"title: {item.get('title')}",
        f"url: {item.get('url')}",
    ]
    if item.get("source_perspective"):
        bits.append(f"configured perspective: {item['source_perspective']}")
    if item.get("authors"):
        bits.append(f"authors: {', '.join(item['authors'][:6])}")
    if item.get("duration_seconds"):
        bits.append(f"duration: {fmt_timestamp(item['duration_seconds'])}")
    if item.get("transcript_source"):
        bits.append(f"text source: {item['transcript_source']}")
    if item.get("transcript_truncated_at_seconds"):
        bits.append(f"NOTE: transcript stops at {fmt_timestamp(item['transcript_truncated_at_seconds'])} (transcription cap)")
    if item.get("thin"):
        bits.append("NOTE: short retained text")
    bits.append(f"retained text: {item.get('text_chars') or len(load_text(item))} characters")
    return "\n".join(bits)


def render_segments(segments: list, max_chars: int | None = None, start: int = 0) -> str:
    """'[s-0012 @ 5:30] text' lines; stops at max_chars (notes truncation)."""
    lines, used = [], 0
    for seg in segments[start:]:
        line = f"[{seg['segment_id']} @ {fmt_timestamp(seg.get('start_seconds'))}] {seg.get('text', '')}"
        if max_chars is not None and used + len(line) > max_chars:
            lines.append(f"[... transcript continues; {len(segments) - len(lines) - start} more segments not shown ...]")
            break
        lines.append(line)
        used += len(line) + 1
    return "\n".join(lines)


def render_item_text(item: dict, max_chars: int) -> str:
    if item.get("segments_path"):
        return render_segments(load_segments(item), max_chars=max_chars)
    text = load_text(item)
    if len(text) > max_chars:
        return text[:max_chars] + f"\n[... text truncated; {len(text) - max_chars} more characters not shown ...]"
    return text


# ----------------------------------------------------------------------------- source notes shared by writers and packaging

MARKER = re.compile(r"\[(0[1-3]-c\d+)\]")


def markers_in(text: str) -> list:
    """Claim markers in order of first appearance."""
    seen, out = set(), []
    for m in MARKER.findall(text or ""):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def evidence_passages(brief: dict, items_by_id: dict, context_chars: int = 600) -> list:
    """For every claim in a brief: resolved passages with context, links and timestamps."""
    out = []
    for claim in brief.get("claims", []):
        entries = []
        for ev in claim.get("evidence", []):
            item = items_by_id.get(ev.get("item_id"))
            if not item:
                entries.append({"item": None, "ok": False, "problem": "unknown item", "ref": ev})
                continue
            res = resolve_evidence(ev, item)
            entry = {"item": item, "ok": res["ok"], "problem": res["problem"], "ref": ev,
                     "passage": res.get("passage"), "start_seconds": res.get("start_seconds"),
                     "end_seconds": res.get("end_seconds"), "context": None,
                     "link": media_link(item, res.get("start_seconds"))}
            loc = ev.get("locator") or {}
            if res["ok"] and loc.get("type") == "text":
                text = normalize_ws(load_text(item))
                q = res.get("exact") or normalize_ws(loc.get("quote") or "")
                i = text.find(q)
                if i >= 0:
                    entry["context"] = text[max(0, i - context_chars): i + len(q) + context_chars]
            elif res["ok"] and loc.get("type") == "segment":
                segs = load_segments(item)
                idx = next((k for k, s in enumerate(segs) if s.get("segment_id") == loc.get("segment_id")), None)
                if idx is not None:
                    window = segs[max(0, idx - 1): idx + 2]
                    entry["context"] = " ".join(f"[{s['segment_id']} @ {fmt_timestamp(s.get('start_seconds'))}] {s.get('text', '')}" for s in window)
            entries.append(entry)
        out.append({"claim": claim, "entries": entries})
    return out


def source_notes_markdown(brief: dict, items_by_id: dict, numbered: dict | None = None) -> str:
    """Audience-facing source list. `numbered` maps claim_id -> reference number; when
    absent the claim ids themselves are shown (internal drafts)."""
    lines = []
    for block in evidence_passages(brief, items_by_id, context_chars=0):
        claim = block["claim"]
        cid = claim["claim_id"]
        label = f"[{numbered[cid]}]" if numbered and cid in numbered else f"[{cid}]"
        kind = {"reported_fact": "reported fact", "source_claim": "source claim", "inference": "our inference"}.get(claim.get("type"), claim.get("type"))
        lines.append(f"- **{label}** ({kind}) {claim.get('statement', '').strip()}")
        for e in block["entries"]:
            item = e["item"]
            if not item:
                lines.append(f"  - unresolved evidence reference: {e['ref']}")
                continue
            date = (item.get("published_at") or "undated")[:10]
            where = f"{item.get('publisher_id')}, *{item.get('title')}* ({date})"
            if e["start_seconds"] is not None:
                where += f", at {fmt_timestamp(e['start_seconds'])}"
            passage = (e.get("passage") or "").strip()
            if len(passage) > 320:
                passage = passage[:317].rstrip() + "..."
            lines.append(f"  - {where}: [{e['link']}]({e['link']})" + (f' — "{passage}"' if passage else ""))
    return "\n".join(lines)
