"""
db/logger.py — Shieldy query logger

Every DNS query that passes through Shieldy gets logged here.
Uses aiosqlite so DB writes never block the DNS server.

Schema:
    queries table — one row per DNS query
        id          INTEGER  autoincrement
        timestamp   TEXT     UTC ISO format
        domain      TEXT     the domain queried
        qtype       TEXT     query type: A, AAAA, MX, etc.
        blocked     INTEGER  1 = blocked, 0 = allowed
        category    TEXT     ads / trackers / malware / custom / "" 
        client_ip   TEXT     always 127.0.0.1 for now (local only)

This is append-only — we never UPDATE or DELETE rows.
Evidence integrity rule from AutoCatcher applies here too :)
"""

import asyncio
import aiosqlite

import config
from utils.logger import get_logger
from utils.timestamp import now_iso

log = get_logger(__name__)

# Module-level DB connection — opened once at startup
_db: aiosqlite.Connection | None = None
_lock = asyncio.Lock()   # prevent concurrent schema init


async def init() -> None:
    """
    Open the SQLite DB and create the queries table if it doesn't exist.
    Call this once at startup before the DNS server starts.
    """
    global _db

    async with _lock:
        if _db is not None:
            return   # already initialized

        _db = await aiosqlite.connect(config.DB_PATH)
        _db.row_factory = aiosqlite.Row   # rows as dict-like objects

        await _db.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                domain      TEXT    NOT NULL,
                qtype       TEXT    NOT NULL DEFAULT 'A',
                blocked     INTEGER NOT NULL DEFAULT 0,
                category    TEXT    NOT NULL DEFAULT '',
                client_ip   TEXT    NOT NULL DEFAULT '127.0.0.1'
            )
        """)

        # Index on domain for fast lookups in stats queries
        await _db.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain
            ON queries (domain)
        """)

        # Index on timestamp for time-range queries (JF graphs by hour/day)
        await _db.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON queries (timestamp)
        """)

        await _db.commit()
        log.info(f"Query log DB ready: {config.DB_PATH}")


async def log_query(
    domain: str,
    blocked: bool,
    category: str = "",
    qtype: str = "A",
    client_ip: str = "127.0.0.1",
) -> None:
    """
    Log a single DNS query. Called by dns/server.py after every query.
    Non-blocking — uses aiosqlite so the DNS server never waits for disk.
    """
    if _db is None:
        log.warning("DB not initialized — call db.logger.init() at startup")
        return

    await _db.execute(
        """
        INSERT INTO queries (timestamp, domain, qtype, blocked, category, client_ip)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (now_iso(), domain, qtype, int(blocked), category, client_ip),
    )
    await _db.commit()


async def close() -> None:
    """Close the DB connection cleanly on shutdown."""
    global _db
    if _db:
        await _db.close()
        _db = None
        log.info("Query log DB closed")
