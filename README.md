# DNS-Shield
> Custom DNS-level blocker and network protection tool.
> Part of Void Weapon — Stage 1.
> Living document — update as the project evolves.

# Overview

## Phase 1 — DNS Core

| Subphase              | Contents                                      | Status       |
|-----------------------|-----------------------------------------------|--------------|
| 1.1 — Foundation      | Project structure, config, utils              | 🔲 Todo      |
| 1.2 — DNS Server      | UDP listener on port 5353, dnslib             | 🔲 Todo      |
| 1.3 — Upstream        | Forward allowed queries to 1.1.1.1 / 9.9.9.9 | 🔲 Todo      |
| 1.4 — Blocklist       | Load .txt / hosts-format lists, set lookup    | 🔲 Todo      |
| 1.5 — Filter Logic    | Block → NXDOMAIN, allow → upstream            | 🔲 Todo      |
| 1.6 — CLI Interface   | main.py (Typer), start/stop/status commands   | 🔲 Todo      |

## Phase 2 — Logging & Stats

| Subphase              | Contents                                      | Status       |
|-----------------------|-----------------------------------------------|--------------|
| 2.1 — Query Logger    | SQLite DB, store domain/timestamp/blocked     | 🔲 Todo      |
| 2.2 — Categories      | Tag queries: ads / trackers / malware / clean | 🔲 Todo      |
| 2.3 — Stats Engine    | Blocked %, top domains, queries/hour          | 🔲 Todo      |
| 2.4 — Export          | CSV / JSON export for JF graphs               | 🔲 Todo      |

## Phase 3 — Web Dashboard

| Subphase              | Contents                                      | Status       |
|-----------------------|-----------------------------------------------|--------------|
| 3.1 — Web Server      | aiohttp shell, serve on localhost:8080        | 🔲 Todo      |
| 3.2 — Stats Page      | Live blocked %, charts, top blocked domains   | 🔲 Todo      |
| 3.3 — Query Log View  | Scrollable log, filterable by category        | 🔲 Todo      |
| 3.4 — Rule Editor     | Add/remove custom block & allow rules         | 🔲 Todo      |
| 3.5 — Blocklist Panel | Toggle lists on/off without restart           | 🔲 Todo      |

## Phase 4 — Original Contribution (JF Core)

| Subphase              | Contents                                      | Status       |
|-----------------------|-----------------------------------------------|--------------|
| 4.1 — Pattern Miner   | Analyze query logs for suspicious patterns    | 🔲 Todo      |
| 4.2 — List Generator  | Auto-generate blocklist from your own data    | 🔲 Todo      |
| 4.3 — Scorer          | Domain reputation score based on behavior     | 🔲 Todo      |
| 4.4 — JF Report       | Auto-generate stats summary for presentation  | 🔲 Todo      |

This is the part that makes Shield *yours* and not just a Pi-hole clone.
Your home network data → your blocklist → your findings. That's original research :)

## Phase 5 — Optional / Future

| Subphase              | Contents                                      | Status       |
|-----------------------|-----------------------------------------------|--------------|
| 5.1 — TUI             | Textual app shell, live query feed            | 🔲 Todo      |
| 5.2 — DoH Support     | DNS-over-HTTPS upstream option                | 🔲 Todo      |
| 5.3 — Void Weapon API | Expose stats to Eye (Watchtower) stage        | 🔲 Todo      |
| 5.4 — Rewrite in Go   | Production-grade speed, mention in JF paper   | 🔲 Todo      |

Not connecting this to a toaster. Probably.

---

# Structure

## Project Structure

```
shield/
├── main.py                  # Entry point — Typer CLI
├── config.py                # Paths, upstream DNS, ports, constants
├── PLAN_TREE.md             # This file
│
├── dns/
│   ├── server.py            # UDP listener on port 5353 (dnslib)
│   ├── filter.py            # Block / allow decision logic
│   └── upstream.py          # Forward queries to 1.1.1.1 / 9.9.9.9
│
├── lists/
│   ├── loader.py            # Parse .txt and hosts-format blocklists
│   ├── categories.py        # Tag domains: ads, trackers, malware
│   └── bundled/             # Shipped-in lists (HaGeZi, OISD, etc.)
│
├── db/
│   ├── logger.py            # Write queries to SQLite
│   └── stats.py             # Aggregate stats queries
│
├── web/
│   ├── server.py            # aiohttp web server
│   ├── routes.py            # API + page routes
│   └── static/              # HTML / CSS / JS dashboard
│
├── contrib/
│   ├── miner.py             # Pattern analysis on query logs
│   ├── gen.py               # Auto-blocklist generator (JF contribution)
│   └── reporter.py          # Generate JF summary report
│
└── utils/
    ├── timestamp.py         # UTC timestamps
    └── logger.py            # Internal app logging
```

---

## Tech Stack

| Layer        | Choice              | Why                                 |
|--------------|---------------------|-------------------------------------|
| Language     | Python              | Eazy, fast to build, great libs     |
| DNS parsing  | dnslib              | Handles DNS packets                 |
| CLI          | Typer               | Typed, clean, auto help             |
| TUI (future) | Textual             | Modern, great on Hyprland           |
| Web          | aiohttp             | Async, lightweight, no Django overhead |
| Storage      | SQLite (aiosqlite)  | One file, no server, portable       |
| Stats/graphs | matplotlib / pandas | For report generation               |
| Terminal UI  | rich                | Pretty output in the CLI            |

---

## Core Design Rules

1. **DNS server and web dashboard run as separate async tasks** — one crash doesn't kill the other.
2. **Blocklists are hot-reloadable** — no restart needed when toggling lists.
3. **Query log is append-only** — never delete or mutate entries, ever.
4. **All timestamps are UTC** — consistent, unambiguous, JF-presentation-safe.
5. **Port 5353 by default** — no root required. Set system DNS to 127.0.0.1:5353.
6. **Config lives in one file** — `config.py` is the single source of truth for paths and settings.

---

# Blocklists

## Bundled Sources

| List          | Category       | Size (approx) | Notes                        |
|---------------|----------------|---------------|------------------------------|
| HaGeZi Multi  | Ads + trackers | ~700k domains | Best general-purpose list    |
| OISD Full     | Ads + malware  | ~800k domains | Very low false positive rate |
| Steven Black  | Ads + fakenews | ~100k domains | Classic, well-maintained     |
| Custom        | own data       | Grows over time | Generated by contrib/gen.py |

---
