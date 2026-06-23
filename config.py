from pathlib import Path

# ── Identity ────────────────────────────────────────────────────────────────
APP_NAME    = "Shieldy-🛡️"
APP_VERSION = "0.1.0"
PART_OF     = "Void Weapon"

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent          # wherever shield/ lives
DB_PATH     = BASE_DIR / "shield.db"         # SQLite query log
LOG_PATH    = BASE_DIR / "shield.log"        # internal app log
LISTS_DIR   = BASE_DIR / "lists" / "bundled" # shipped-in blocklists
CUSTOM_LIST = BASE_DIR / "lists" / "custom.txt" # your own rules

# ── DNS server ──────────────────────────────────────────────────────────────
DNS_HOST      = "127.0.0.1"
DNS_PORT      = 5353           # no root needed (53 needs root)
DNS_UPSTREAM  = "1.1.1.1"     # Cloudflare — swap to 9.9.9.9 (Quad9) if you want
DNS_UPSTREAM2 = "9.9.9.9"     # fallback upstream
DNS_TIMEOUT   = 5              # seconds before upstream gives up

# ── Web dashboard ───────────────────────────────────────────────────────────
WEB_HOST = "127.0.0.1"
WEB_PORT = 8080                # open http://localhost:8080 in browser

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"             # DEBUG / INFO / WARNING / ERROR

# ── Blocklist behaviour ─────────────────────────────────────────────────────
# Categories used for tagging blocked domains in the DB
CATEGORIES = ["ads", "trackers", "malware", "fakenews", "custom"]

# Default block response — NXDOMAIN means "this domain does not exist"
# Alternative: return 0.0.0.0 (null IP) — NXDOMAIN is cleaner
BLOCK_MODE = "NXDOMAIN"