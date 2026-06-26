"""
db/stats.py — query log stats for the dashboard and JF report

All functions are async and read from the same SQLite DB as logger.py.
These are the numbers you'll put in your JF presentation :)
"""

import aiosqlite
import config
from utils.logger import get_logger

log = get_logger(__name__)


async def totals() -> dict:
    """
    Overall stats since Shieldy started logging.

    Returns:
        {
          "total":   int,
          "blocked": int,
          "allowed": int,
          "block_pct": float
        }
    """
    async with aiosqlite.connect(config.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT COUNT(*) FROM queries") as cur:
            total = (await cur.fetchone())[0]
        async with conn.execute(
            "SELECT COUNT(*) FROM queries WHERE blocked = 1"
        ) as cur:
            blocked = (await cur.fetchone())[0]

    allowed = total - blocked
    pct     = round((blocked / total * 100), 2) if total > 0 else 0.0

    return {
        "total":     total,
        "blocked":   blocked,
        "allowed":   allowed,
        "block_pct": pct,
    }


async def by_category() -> list[dict]:
    """
    Breakdown of blocked queries by category.
    Great for a pie chart in your JF presentation.

    Returns list of {"category": str, "count": int}
    """
    async with aiosqlite.connect(config.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("""
            SELECT category, COUNT(*) as count
            FROM queries
            WHERE blocked = 1
            GROUP BY category
            ORDER BY count DESC
        """) as cur:
            rows = await cur.fetchall()

    return [{"category": r["category"] or "unknown", "count": r["count"]}
            for r in rows]


async def top_blocked(limit: int = 10) -> list[dict]:
    """
    Top N most-blocked domains.
    Shows which sites are trying to track you the most.

    Returns list of {"domain": str, "count": int, "category": str}
    """
    async with aiosqlite.connect(config.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("""
            SELECT domain, category, COUNT(*) as count
            FROM queries
            WHERE blocked = 1
            GROUP BY domain
            ORDER BY count DESC
            LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()

    return [{"domain": r["domain"], "count": r["count"],
             "category": r["category"]} for r in rows]


async def queries_over_time(hours: int = 24) -> list[dict]:
    """
    Query volume grouped by hour for the last N hours.
    Use this to draw a timeline graph in the JF report.

    Returns list of {"hour": str, "total": int, "blocked": int}
    """
    async with aiosqlite.connect(config.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(f"""
            SELECT
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                COUNT(*) as total,
                SUM(blocked) as blocked
            FROM queries
            WHERE timestamp >= datetime('now', '-{hours} hours')
            GROUP BY hour
            ORDER BY hour ASC
        """) as cur:
            rows = await cur.fetchall()

    return [{"hour": r["hour"], "total": r["total"],
             "blocked": r["blocked"] or 0} for r in rows]


async def recent(limit: int = 50) -> list[dict]:
    """
    Most recent N queries — for the live log view in the dashboard.

    Returns list of {"timestamp", "domain", "qtype", "blocked", "category"}
    """
    async with aiosqlite.connect(config.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("""
            SELECT timestamp, domain, qtype, blocked, category
            FROM queries
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()

    return [dict(r) for r in rows]