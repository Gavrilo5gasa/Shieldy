f# Shield — Learning Roadmap
> Resources to understand and build this project on your own.
> Roughly in order — don't skip ahead, each row builds on the last.

---

## 1. Python Basics (if not solid yet)

| What                          | Link                                                                      | Why it matters for this project              |
|-------------------------------|---------------------------------------------------------------------------|----------------------------------------------|
| Python official tutorial      | https://docs.python.org/3/tutorial/                                       | Foundation for everything                    |
| f-strings & string formatting | https://realpython.com/python-f-strings/                                  | Used everywhere in logs and stats output     |
| Pathlib (file paths)          | https://realpython.com/python-pathlib/                                    | How we handle blocklist files and the DB     |
| Dataclasses                   | https://realpython.com/python-data-classes/                               | How query log entries are structured         |
| Type hints                    | https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html                | Makes code readable and catches bugs early   |
| Async / await basics          | https://realpython.com/async-io-python/                                   | DNS server + web dashboard run concurrently  |

---

## 2. The Standard Library (built-in, no install needed)

| What          | Link                                               | Where used                          |
|---------------|----------------------------------------------------|-------------------------------------|
| `socket`      | https://docs.python.org/3/library/socket.html      | UDP listener under the hood         |
| `asyncio`     | https://docs.python.org/3/library/asyncio.html     | Async core for server + dashboard   |
| `sqlite3`     | https://docs.python.org/3/library/sqlite3.html     | Query logging in db/logger.py       |
| `json`        | https://docs.python.org/3/library/json.html        | Config and stats export             |
| `pathlib`     | https://docs.python.org/3/library/pathlib.html     | All file/folder work                |
| `logging`     | https://docs.python.org/3/library/logging.html     | utils/logger.py                     |
| `datetime`    | https://docs.python.org/3/library/datetime.html    | utils/timestamp.py                  |
| `dataclasses` | https://docs.python.org/3/library/dataclasses.html | Query log entry model               |
| `csv`         | https://docs.python.org/3/library/csv.html         | Export logs for JF graphs           |

---

## 3. Key Third-Party Libraries (you will install these)

| Library    | Install                  | Docs                              | Used in                              |
|------------|--------------------------|-----------------------------------|--------------------------------------|
| dnslib     | `pip install dnslib`     | https://github.com/paulc/dnslib   | dns/server.py — DNS packet parsing   |
| aiohttp    | `pip install aiohttp`    | https://docs.aiohttp.org          | web/server.py — dashboard            |
| aiosqlite  | `pip install aiosqlite`  | https://aiosqlite.omnilib.dev     | db/logger.py — async SQLite          |
| Typer      | `pip install typer`      | https://typer.tiangolo.com        | main.py — CLI                        |
| Rich       | `pip install rich`       | https://rich.readthedocs.io       | Pretty terminal output (with Typer)  |
| pandas     | `pip install pandas`     | https://pandas.pydata.org/docs    | contrib/miner.py — log analysis      |
| matplotlib | `pip install matplotlib` | https://matplotlib.org/stable     | contrib/reporter.py — JF graphs      |
| Textual    | `pip install textual`    | https://textual.textualize.io     | TUI in Phase 5 (optional)            |

---

## 4. DNS — what you're actually building

| Concept                  | Good explanation                                                          | Where it shows up                     |
|--------------------------|---------------------------------------------------------------------------|---------------------------------------|
| How DNS works            | https://howdns.works                                                      | Everything — read this first          |
| DNS record types         | https://www.cloudflare.com/learning/dns/dns-records/                      | dns/server.py — parsing queries       |
| What NXDOMAIN means      | https://www.cloudflare.com/learning/dns/what-is-dns/                      | dns/filter.py — block response        |
| Hosts file format        | https://en.wikipedia.org/wiki/Hosts_(file)                                | lists/loader.py — parsing blocklists  |
| DNS-over-HTTPS (DoH)     | https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/      | Phase 5.2 upstream option             |
| dnslib walkthrough       | https://github.com/paulc/dnslib/tree/master/examples                      | dns/server.py — your actual code      |

---

## 5. Async Python — the hard part

| What                          | Link                                                                | Where it shows up                        |
|-------------------------------|---------------------------------------------------------------------|------------------------------------------|
| asyncio intro                 | https://realpython.com/async-io-python/                             | dns/server.py + web/server.py            |
| asyncio UDP protocol          | https://docs.python.org/3/library/asyncio-protocol.html             | How the DNS listener is actually built   |
| aiosqlite usage               | https://aiosqlite.omnilib.dev/en/stable/                            | db/logger.py — non-blocking DB writes    |
| Running tasks concurrently    | https://docs.python.org/3/library/asyncio-task.html#asyncio.gather  | main.py — DNS + web run at the same time |

---

## 6. SQLite & data

| What                    | Link                                                              | Where it shows up                    |
|-------------------------|-------------------------------------------------------------------|--------------------------------------|
| SQLite basics           | https://www.sqlitetutorial.net                                    | db/logger.py, db/stats.py            |
| sqlite3 Python docs     | https://docs.python.org/3/library/sqlite3.html                    | All DB work                          |
| pandas for data analysis| https://realpython.com/pandas-python-explore-dataset/             | contrib/miner.py — finding patterns  |
| matplotlib basics       | https://matplotlib.org/stable/tutorials/introductory/pyplot.html  | contrib/reporter.py — JF graphs      |

---

## 7. Git — version control (essential)

| What                           | Link                                                            |
|--------------------------------|-----------------------------------------------------------------|
| Git basics (commits, branches) | https://git-scm.com/book/en/v2/Getting-Started-Git-Basics      |
| Good commit messages           | https://www.conventionalcommits.org                             |
| .gitignore for Python          | https://github.com/github/gitignore/blob/main/Python.gitignore  |

**Start this now.** Run `git init` in the shield/ folder and commit after each subphase.

---

## 8. Arch Linux specific

| What                                | Link                                                         |
|-------------------------------------|--------------------------------------------------------------|
| Python virtual environments on Arch | https://wiki.archlinux.org/title/Python/Virtual_environment  |
| systemd user services               | https://wiki.archlinux.org/title/Systemd/User                |
| Setting custom DNS on Arch          | https://wiki.archlinux.org/title/Domain_name_resolution      |
| NetworkManager DNS config           | https://wiki.archlinux.org/title/NetworkManager#DNS          |

The systemd one matters — eventually you'll want Shield to auto-start on boot as a user service, not a root service.

---

## 9. General Python learning (good to have open)

| What                                           | Link                                                                      |
|------------------------------------------------|---------------------------------------------------------------------------|
| Automate the Boring Stuff                      | https://automatetheboringstuff.com/#toc                                   |
| CS50's Introduction to Programming with Python | https://cs50.harvard.edu/python/                                          |
| Python Programming MOOC 2026                   | https://programming-26.mooc.fi/                                           |
| Corey Schafer Python Course                    | https://www.youtube.com/playlist?list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7 |
| PythonDiscord Library                          | https://www.pythondiscord.com/resources/                                  |

---

## Quick reference — things you'll type a lot

```bash
# Create and activate a venv (do this once)
python3 -m venv .venv
source .venv/bin/activate

# Install all deps
pip install dnslib aiohttp aiosqlite typer rich pandas matplotlib

# Start Shield
python3 main.py start

# Check it's intercepting DNS
dig @127.0.0.1 -p 5353 example.com

# Check a known ad domain is blocked
dig @127.0.0.1 -p 5353 doubleclick.net

# See your query log
sqlite3 shield.db "SELECT * FROM queries ORDER BY timestamp DESC LIMIT 20;"

# Export stats to CSV
python3 main.py export --format csv

# Run the blocklist generator
python3 -m contrib.gen --days 7
```
