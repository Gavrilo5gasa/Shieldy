from datetime import datetime, timezone


def now() -> datetime:
    """Current time in UTC. Always use this — never datetime.now() without tz."""
    return datetime.now(timezone.utc)


def now_str() -> str:
    """UTC timestamp as a readable string. Used in log entries and filenames."""
    return now().strftime("%Y-%m-%d %H:%M:%S UTC")


def now_filename() -> str:
    """UTC timestamp safe for filenames — no spaces or colons."""
    return now().strftime("%Y-%m-%dT%H-%M-%SZ")


def now_iso() -> str:
    """UTC timestamp in ISO 8601 format. Used for JSON / DB storage."""
    return now().isoformat()
