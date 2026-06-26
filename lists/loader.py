"""
lists/loader.py — blocklist file parser

Supports two common formats:

  1. Hosts format (most common):
       0.0.0.0 doubleclick.net
       127.0.0.1 tracking.evil.com
       # this is a comment

  2. Plain domain list:
       doubleclick.net
       tracking.evil.com
       # this is a comment

Both formats are used in the wild — HaGeZi, OISD, Steven Black all use
one of these. We autodetect which one based on whether the line starts
with an IP address.

Usage:
    from lists.loader import load_all
    load_all()   # reads lists/bundled/ + lists/custom.txt, calls filter.load()
"""

import re
from pathlib import Path

import config
from shieldy_dns.filter import load
from utils.logger import get_logger

log = get_logger(__name__)

# Regex to detect a hosts-format line: starts with an IP address
_IP_PREFIX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}\s+")

# Map list filename keywords → category tag
# e.g. "hagezi-ads.txt" → "ads", "oisd-malware.txt" → "malware"
_CATEGORY_HINTS: dict[str, str] = {
    "ads":      "ads",
    "tracker":  "trackers",
    "tracking": "trackers",
    "malware":  "malware",
    "phishing": "malware",
    "fakenews": "fakenews",
    "fake":     "fakenews",
    "custom":   "custom",
}


def _detect_category(path: Path) -> str:
    """Guess category from filename. Falls back to 'ads' if unknown."""
    name = path.stem.lower()
    for keyword, cat in _CATEGORY_HINTS.items():
        if keyword in name:
            return cat
    return "ads"   # safe default


def _parse_file(path: Path, category: str) -> dict[str, str]:
    """
    Parse a single blocklist file.
    Returns dict of {domain: category}.
    Skips comments, empty lines, localhost, and invalid entries.
    """
    domains: dict[str, str] = {}
    skipped = 0

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError as e:
        log.error(f"Could not read {path}: {e}")
        return {}

    for line in lines:
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith("#") or line.startswith("!"):
            continue

        # Strip inline comments
        if "#" in line:
            line = line[:line.index("#")].strip()

        # Hosts format: "0.0.0.0 doubleclick.net" → extract domain
        if _IP_PREFIX.match(line):
            parts = line.split()
            if len(parts) < 2:
                continue
            domain = parts[1].lower()
        else:
            # Plain domain list: "doubleclick.net"
            domain = line.lower()

        # Skip localhost and bare TLDs
        if domain in ("localhost", "localhost.localdomain", "broadcasthost"):
            continue
        if "." not in domain:
            continue

        domains[domain] = category

    log.debug(f"Parsed {path.name}: {len(domains):,} domains [{category}] "
              f"(skipped {skipped})")
    return domains


def load_all(
    lists_dir: Path | None = None,
    custom_list: Path | None = None,
    allowlist: set[str] | None = None,
) -> int:
    """
    Load all blocklists from lists/bundled/ and lists/custom.txt.
    Calls filter.load() with the combined result.

    Returns total number of domains loaded.
    """
    lists_dir   = lists_dir   or config.LISTS_DIR
    custom_list = custom_list or config.CUSTOM_LIST

    combined: dict[str, str] = {}

    # ── Bundled lists ────────────────────────────────────────────────────────
    if lists_dir.exists():
        txt_files = sorted(lists_dir.glob("*.txt"))
        if not txt_files:
            log.warning(f"No .txt blocklists found in {lists_dir} — "
                        f"download some and put them there!")
        for path in txt_files:
            category = _detect_category(path)
            domains  = _parse_file(path, category)
            combined.update(domains)   # later lists overwrite earlier ones
            log.info(f"Loaded {path.name}: {len(domains):,} domains [{category}]")
    else:
        log.warning(f"Bundled lists directory not found: {lists_dir}")

    # ── Custom list (your own rules) ─────────────────────────────────────────
    if custom_list.exists():
        custom_domains = _parse_file(custom_list, "custom")
        combined.update(custom_domains)
        log.info(f"Loaded custom.txt: {len(custom_domains):,} domains")
    else:
        log.debug(f"No custom list found at {custom_list} — that's fine")

    # ── Hand off to filter.py ────────────────────────────────────────────────
    load(combined, allowlist or set())
    log.info(f"Total blocklist: {len(combined):,} domains across all lists")

    return len(combined)
