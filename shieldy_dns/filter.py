"""
dns/filter.py — block / allow decision

is_blocked(domain) is the single function everything calls.
It checks the domain against the loaded blocklist set and returns:
  (True,  "category")  — block it
  (False, "")          — allow it, forward to upstream

The blocklist is a dict:  domain → category
  e.g. {"doubleclick.net": "ads", "tracking.evil.com": "trackers"}

We also check subdomains:
  "sub.doubleclick.net" matches "doubleclick.net" in the blocklist
  This is how real DNS blockers work — block the root, catch all subs.
"""

from utils.logger import get_logger

log = get_logger(__name__)

# Module-level blocklist — loaded once by lists/loader.py at startup
# Maps domain → category string
# e.g. {"doubleclick.net": "ads", "malware.example.com": "malware"}
_blocklist: dict[str, str] = {}

# Allowlist — domains that should NEVER be blocked even if in a blocklist
# Add things here that keep getting false-positived
_allowlist: set[str] = set()


def load(blocklist: dict[str, str], allowlist: set[str] | None = None) -> None:
    """
    Called once at startup by lists/loader.py.
    Replaces the in-memory blocklist and allowlist.
    """
    global _blocklist, _allowlist
    _blocklist = blocklist
    _allowlist = allowlist or set()
    log.info(f"Blocklist loaded: {len(_blocklist):,} domains | "
             f"Allowlist: {len(_allowlist)} entries")


def is_blocked(domain: str) -> tuple[bool, str]:
    """
    Check if a domain should be blocked.

    Returns:
        (True,  category)  — block, reply NXDOMAIN
        (False, "")        — allow, forward to upstream

    Subdomain matching:
        "sub.tracker.com" → checks "sub.tracker.com", then "tracker.com"
        Stops at the root so we don't block everything accidentally.
    """
    domain = domain.lower().rstrip(".")

    # Allowlist check first — always takes priority
    if domain in _allowlist:
        return False, ""

    # Exact match
    if domain in _blocklist:
        return True, _blocklist[domain]

    # Subdomain match — walk up the domain tree
    # "a.b.c.com" → try "b.c.com" → try "c.com" → stop
    parts = domain.split(".")
    for i in range(1, len(parts) - 1):   # -1 so we don't check bare TLDs
        parent = ".".join(parts[i:])
        if parent in _blocklist:
            return True, _blocklist[parent]

    return False, ""


def add_to_allowlist(domain: str) -> None:
    """Runtime allowlist — survives until restart. UI calls this."""
    _allowlist.add(domain.lower().rstrip("."))
    log.info(f"Allowlisted: {domain}")


def stats() -> dict:
    """Quick summary for the dashboard."""
    from collections import Counter
    cats = Counter(_blocklist.values())
    return {
        "total_blocked_domains": len(_blocklist),
        "by_category": dict(cats),
        "allowlist_size": len(_allowlist),
    }