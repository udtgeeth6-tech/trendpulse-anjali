"""
02_clean.py — Data Cleaning & Normalisation
============================================
Reads raw/raw_data.json and applies the following cleaning steps:

  1. Schema validation   — drops records missing required fields
  2. Deduplication       — removes exact-URL duplicates
  3. Text normalisation  — strips HTML, collapses whitespace, truncates
  4. Score normalisation — min-max per source (0–100 float)
  5. Language tagging    — fills missing language with "Unknown"
  6. Timestamp parsing   — ensures ISO-8601 datetimes; bad ones → None

Output: clean/clean_data.json  +  clean/cleaning_report.json
"""

import os
import re
import json
import html
import logging
from datetime import datetime, timezone
from collections import defaultdict

# ── Config ───────────────────────────────────────────────────────────────────
RAW_FILE = os.path.join("raw", "raw_data.json")
CLEAN_DIR = "clean"
CLEAN_FILE = os.path.join(CLEAN_DIR, "clean_data.json")
REPORT_FILE = os.path.join(CLEAN_DIR, "cleaning_report.json")

REQUIRED_FIELDS = {"source", "id", "title", "url", "score"}
MAX_TITLE_LEN = 200
MAX_DESC_LEN = 500

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Text helpers ──────────────────────────────────────────────────────────────
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return text.strip()


def normalise_text(text: str, max_len: int = None) -> str:
    """Collapse whitespace, strip, optionally truncate."""
    text = strip_html(text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if max_len and len(text) > max_len:
        text = text[:max_len].rstrip() + "…"
    return text


# ── Timestamp helper ──────────────────────────────────────────────────────────
def parse_iso(ts: str) -> str | None:
    """Return a normalised ISO-8601 string, or None if unparseable."""
    if not ts:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(ts, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
    return None


# ── Score normalisation ───────────────────────────────────────────────────────
def minmax_normalise(records: list[dict]) -> list[dict]:
    """
    Adds `score_norm` (0.0–100.0) per source so scores are comparable
    across GitHub stars, HN points, and Wikipedia views.
    """
    by_source: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_source[r["source"]].append(r)

    for source, group in by_source.items():
        scores = [r["score"] for r in group]
        lo, hi = min(scores), max(scores)
        span = hi - lo if hi != lo else 1
        for r in group:
            r["score_norm"] = round((r["score"] - lo) / span * 100, 2)

    return records


# ── Validation ────────────────────────────────────────────────────────────────
def validate(record: dict) -> tuple[bool, str]:
    """Return (is_valid, reason). reason is '' if valid."""
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        return False, f"missing fields: {missing}"
    if not isinstance(record.get("score"), (int, float)):
        return False, "score is not numeric"
    if not record.get("title", "").strip():
        return False, "empty title"
    if not record.get("url", "").startswith("http"):
        return False, "invalid url"
    return True, ""


# ── Main cleaning pipeline ────────────────────────────────────────────────────
def clean(records: list[dict]) -> tuple[list[dict], dict]:
    report = {
        "input_count": len(records),
        "dropped_schema": 0,
        "dropped_duplicate": 0,
        "normalised_timestamps_fixed": 0,
        "output_count": 0,
        "per_source": {},
    }

    # 1. Schema validation
    valid, invalid = [], []
    for r in records:
        ok, reason = validate(r)
        if ok:
            valid.append(r)
        else:
            invalid.append((r, reason))
            log.debug("DROP (schema) — %s: %s", r.get("id"), reason)

    report["dropped_schema"] = len(invalid)
    log.info("Schema: kept %d / dropped %d", len(valid), len(invalid))

    # 2. Deduplication by URL
    seen_urls: set[str] = set()
    deduped = []
    for r in valid:
        url = r["url"].rstrip("/")
        if url not in seen_urls:
            seen_urls.add(url)
            deduped.append(r)
        else:
            report["dropped_duplicate"] += 1
    log.info("Dedup: kept %d / dropped %d duplicates", len(deduped), report["dropped_duplicate"])

    # 3. Text normalisation
    for r in deduped:
        r["title"] = normalise_text(r.get("title", ""), MAX_TITLE_LEN)
        r["description"] = normalise_text(r.get("description", ""), MAX_DESC_LEN)
        r["language"] = (r.get("language") or "Unknown").strip() or "Unknown"

    # 4. Timestamp parsing
    for r in deduped:
        original = r.get("created_at")
        parsed = parse_iso(original or "")
        if original and not parsed:
            report["normalised_timestamps_fixed"] += 1
            log.debug("Timestamp fixed: %s → None", original)
        r["created_at"] = parsed
        r["fetched_at"] = parse_iso(r.get("fetched_at") or "")

    # 5. Score normalisation
    deduped = minmax_normalise(deduped)

    # 6. Per-source summary
    for r in deduped:
        src = r["source"]
        if src not in report["per_source"]:
            report["per_source"][src] = {"count": 0, "avg_score": 0.0, "scores": []}
        report["per_source"][src]["count"] += 1
        report["per_source"][src]["scores"].append(r["score"])

    for src, info in report["per_source"].items():
        sc = info.pop("scores")
        info["avg_score"] = round(sum(sc) / len(sc), 2) if sc else 0.0
        info["max_score"] = max(sc) if sc else 0

    report["output_count"] = len(deduped)
    return deduped, report


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    log.info("=== Stage 2: Clean ===")

    with open(RAW_FILE, encoding="utf-8") as fh:
        raw = json.load(fh)

    records = raw.get("records", [])
    log.info("Loaded %d raw records from %s", len(records), RAW_FILE)

    clean_records, report = clean(records)

    # Write clean data
    payload = {
        "cleaned_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(clean_records),
        "records": clean_records,
    }
    with open(CLEAN_FILE, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    log.info("Clean data → %s (%d records)", CLEAN_FILE, len(clean_records))

    # Write report
    with open(REPORT_FILE, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    log.info("Cleaning report → %s", REPORT_FILE)
    log.info("=== Stage 2 complete ===\n")


if __name__ == "__main__":
    main()
