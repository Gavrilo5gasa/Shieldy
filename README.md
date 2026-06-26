# Shieldy 🛡️
> Custom DNS-level blocker and network protection tool.
> Part of Project Void Weapon — Stage 1 · Shield.
> Built from scratch in Python — not a Pi-hole clone.

---

## What it does

Shieldy sits between your computer and the internet and intercepts every DNS query your machine makes.
If the domain is on a blocklist — ads, trackers, malware — it replies with NXDOMAIN instantly (0ms, never touches the network).
If it's clean, it forwards the query to a real upstream resolver (1.1.1.1 / 9.9.9.9) and returns the answer.

Everything that passes through gets logged to a local SQLite database so you can see exactly what your machine is talking to.

---

## Quick start

```bash
# 1. Clone and enter
git clone https://github.com/Gavrilo5gasa/Shieldy
cd Shieldy

# 2. Install dependencies
pip install dnslib aiohttp aiosqlite typer rich

# 3. Download a blocklist
mkdir -p lists/bundled
curl -o lists/bundled/hagezi-ads.txt \
  https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/pro.txt

# 4. Start Shieldy
PYTHONPATH=. python3 main.py start --no-web

# 5. Test it (in another terminal)
dig @127.0.0.1 -p 5353 fls.doubleclick.net   # → NXDOMAIN (blocked, 0ms)
dig @127.0.0.1 -p 5353 google.com            # → real IP (allowed)
```

To use Shieldy as your actual system DNS, set your DNS to `127.0.0.1` port `5353` in NetworkManager.

---

## Commands

```bash
# Start (DNS only)
PYTHONPATH=. python3 main.py start --no-web

# Start (DNS + web dashboard)
PYTHONPATH=. python3 main.py start

# Live stats
PYTHONPATH=. python3 main.py status

# Stop a running instance
PYTHONPATH=. python3 main.py stop

# Allowlist a domain (runtime, resets on restart)
PYTHONPATH=. python3 main.py allowlist safe.example.com
```

---

## Project structure

```
Shieldy/
├── main.py                    # Entry point — Typer CLI
├── config.py                  # Paths, ports, constants — edit this
├── PLAN_TREE.md               # Project roadmap
├── LEARNING.md                # Learning resources
│
├── shieldy_dns/
│   ├── server.py              # Async UDP listener on port 5353
│   ├── filter.py              # Block / allow decision logic
│   └── upstream.py            # Forward queries to 1.1.1.1 / 9.9.9.9
│
├── lists/
│   ├── loader.py              # Parse .txt and hosts-format blocklists
│   └── bundled/               # Drop blocklist .txt files here
│
├── db/
│   ├── logger.py              # Write every query to SQLite
│   └── stats.py               # Aggregate stats for dashboard + JF report
│
├── web/
│   ├── server.py              # aiohttp dashboard (Phase 3)
│   └── static/                # HTML / CSS / JS
│
├── contrib/
│   ├── miner.py               # Pattern analysis on query logs (Phase 4)
│   ├── gen.py                 # Auto-blocklist generator (Phase 4)
│   └── reporter.py            # JF summary report generator (Phase 4)
│
└── utils/
    ├── timestamp.py           # UTC timestamps
    └── logger.py              # Internal app logging (Rich)
```

---

## Tech stack

| Layer        | Choice              | Why                                      |
|--------------|---------------------|------------------------------------------|
| Language     | Python              | Fast to build, great async libs          |
| DNS parsing  | dnslib              | Handles DNS packets so you don't have to |
| CLI          | Typer               | Typed, clean, auto-generated help        |
| Web          | aiohttp             | Async, lightweight                       |
| Storage      | SQLite + aiosqlite  | One file, no server, portable            |
| Terminal UI  | Rich                | Pretty output in the CLI                 |

---

## Blocklists

Drop any `.txt` blocklist file into `lists/bundled/`. Shieldy auto-detects the format (hosts-format or plain domain list) and the category from the filename.

| Filename keyword | Category tagged as |
|------------------|--------------------|
| `ads`, `ad`      | ads                |
| `tracker`        | trackers           |
| `malware`        | malware            |
| `fakenews`       | fakenews           |
| `custom`         | custom             |

**Recommended lists:**

| List          | URL                                                                          |
|---------------|------------------------------------------------------------------------------|
| HaGeZi Pro    | https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/pro.txt   |
| OISD Full     | https://dbl.oisd.nl/basic/                                                   |
| Steven Black  | https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts             |

Add your own rules to `lists/custom.txt` — one domain per line.

---

## Core design rules

1. **DNS server and web dashboard run as separate async tasks** — one crash doesn't kill the other.
2. **Blocklists are hot-reloadable** — no restart needed when toggling lists.
3. **Query log is append-only** — never delete or mutate entries, ever.
4. **All timestamps are UTC** — consistent, unambiguous.
5. **Port 5353 by default** — no root required.
6. **Config lives in one file** — `config.py` is the single source of truth.

---

## Part of Void Weapon

| Stage  | Name        | What it does                              | Status      |
|--------|-------------|-------------------------------------------|-------------|
| 🛡️ 1   | Shieldy     | DNS blocker — block at the network level  | 🔨 Building |
| ⚔️ 2   | AutoCatcher | Evidence collection for online predators  | 🔨 Building |
| 👁️ 3   | Watchtower  | Network monitoring & threat intelligence  | 🔲 Planned  |

### Watchtower — planned features
- Live news intelligence across custom modules (cybersecurity, darkweb, world, local)
- World map showing where threats and alerts are originating
- Lockdown system — firewall, ghost mode, killswitch, DNS lock toggles
- System monitor — CPU, RAM, disk, network live stats
- **Shieldy integration** — Watchtower reads Shieldy's SQLite DB and displays
  DNS block stats, block rate spikes, and top threat categories as a live panel
- Threat intelligence — cross-reference Shieldy's blocked domains against known
  malware feeds and alert on anomalies

---

## Status

Phase 1 — DNS Core ✅ Complete
Phase 2 — Logging & Stats 🔨 In progress
Phase 3 — Web Dashboard 🔲 Todo
Phase 4 — Original Contribution (JF) 🔲 Todo
Phase 5 — Optional / Future 🔲 Todo
