"""
main.py — Shieldy 🛡️ entry point

Commands:
    python3 main.py start     — start the DNS server + web dashboard
    python3 main.py status    — show live stats from the query log
    python3 main.py stop      — stop a running Shieldy instance
    python3 main.py allowlist — add a domain to the allowlist
"""

import asyncio
import signal
import sys
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config
from lists.loader import load_all
from db.logger import init as db_init, close as db_close
from shieldy_dns.server import run_server
from utils.logger import get_logger
from utils.timestamp import now_str

log     = console = Console()
app     = typer.Typer(help="Shieldy 🛡️ — custom DNS blocker · part of Void Weapon")
PID_FILE = config.BASE_DIR / "shieldy.pid"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _write_pid() -> None:
    PID_FILE.write_text(str(asyncio.get_event_loop().os_getpid()
                            if hasattr(asyncio.get_event_loop(), 'os_getpid')
                            else __import__('os').getpid()))


def _read_pid() -> int | None:
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except ValueError:
            return None
    return None


def _clear_pid() -> None:
    if PID_FILE.exists():
        PID_FILE.unlink()


def _banner() -> None:
    console.print(Panel(
        f"[bold cyan]Shieldy 🛡️[/bold cyan]  v{config.APP_VERSION}"
        f"DNS   [green]{config.DNS_HOST}:{config.DNS_PORT}[/green]  →  upstream [yellow]{config.DNS_UPSTREAM}[/yellow]\n"
        f"Web   [green]http://{config.WEB_HOST}:{config.WEB_PORT}[/green]\n"
        f"DB    [dim]{config.DB_PATH}[/dim]",
        title="Starting",
        border_style="cyan",
    ))


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command()
def start(
    no_web: bool = typer.Option(False, "--no-web", help="Skip the web dashboard"),
) -> None:
    """Start the Shieldy DNS server (and web dashboard)."""

    _banner()

    async def _run() -> None:
        # 1. Init DB
        await db_init()

        # 2. Load blocklists
        total = load_all()
        console.print(f"[green]✓[/green] Blocklist ready: [bold]{total:,}[/bold] domains")

        # 3. Graceful shutdown on Ctrl+C
        loop = asyncio.get_running_loop()

        def _shutdown():
            console.print("\n[yellow]Shutting down Shieldy...[/yellow]")
            for task in asyncio.all_tasks(loop):
                task.cancel()

        loop.add_signal_handler(signal.SIGINT,  _shutdown)
        loop.add_signal_handler(signal.SIGTERM, _shutdown)

        # 4. Write PID so `shieldy stop` can find us
        import os
        PID_FILE.write_text(str(os.getpid()))

        try:
            if no_web:
                await run_server()
            else:
                # Run DNS server and web dashboard concurrently
                from web.server import run_web
                await asyncio.gather(
                    run_server(),
                    run_web(),
                    return_exceptions=True,
                )
        finally:
            _clear_pid()
            await db_close()
            console.print("[green]Shieldy stopped cleanly.[/green]")

    asyncio.run(_run())


@app.command()
def status() -> None:
    """Show live stats from the Shieldy query log."""

    async def _show() -> None:
        from db import stats

        pid = _read_pid()
        running = "[bold green]● Running[/bold green]" if pid else "[red]○ Stopped[/red]"
        console.print(Panel(
            f"Status: {running}  {f'(PID {pid})' if pid else ''}\n"
            f"Time:   {now_str()}",
            title="Shieldy 🛡️  Status",
            border_style="cyan",
        ))

        if not config.DB_PATH.exists():
            console.print("[yellow]No query log found — has Shieldy run yet?[/yellow]")
            return

        t = await stats.totals()

        # ── Summary ──────────────────────────────────────────────────────────
        console.print(f"\n  Total queries : [bold]{t['total']:,}[/bold]")
        console.print(f"  Blocked       : [bold red]{t['blocked']:,}[/bold red] "
                      f"([bold]{t['block_pct']}%[/bold])")
        console.print(f"  Allowed       : [bold green]{t['allowed']:,}[/bold green]")

        # ── By category ──────────────────────────────────────────────────────
        cats = await stats.by_category()
        if cats:
            console.print()
            cat_table = Table(title="Blocked by category", border_style="dim")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count",    justify="right")
            for row in cats:
                cat_table.add_row(row["category"], str(row["count"]))
            console.print(cat_table)

        # ── Top blocked ──────────────────────────────────────────────────────
        top = await stats.top_blocked(10)
        if top:
            top_table = Table(title="Top 10 blocked domains", border_style="dim")
            top_table.add_column("Domain",   style="red")
            top_table.add_column("Category", style="cyan")
            top_table.add_column("Hits",     justify="right")
            for row in top:
                top_table.add_row(row["domain"], row["category"], str(row["count"]))
            console.print(top_table)

        # ── Recent queries ───────────────────────────────────────────────────
        recent = await stats.recent(10)
        if recent:
            rec_table = Table(title="Last 10 queries", border_style="dim")
            rec_table.add_column("Time",     style="dim")
            rec_table.add_column("Domain")
            rec_table.add_column("Type",     style="dim")
            rec_table.add_column("Result")
            for row in recent:
                result = "[red]BLOCK[/red]" if row["blocked"] else "[green]ALLOW[/green]"
                rec_table.add_row(
                    row["timestamp"][:19],
                    row["domain"],
                    row["qtype"],
                    result,
                )
            console.print(rec_table)

    asyncio.run(_show())


@app.command()
def stop() -> None:
    """Stop a running Shieldy instance."""
    import os

    pid = _read_pid()
    if pid is None:
        console.print("[yellow]Shieldy doesn't appear to be running (no PID file).[/yellow]")
        raise typer.Exit(1)

    try:
        os.kill(pid, signal.SIGTERM)
        _clear_pid()
        console.print(f"[green]✓ Sent SIGTERM to Shieldy (PID {pid})[/green]")
    except ProcessLookupError:
        console.print(f"[yellow]Process {pid} not found — cleaning up stale PID file.[/yellow]")
        _clear_pid()


@app.command()
def allowlist(
    domain: str = typer.Argument(..., help="Domain to allow e.g. safe.example.com"),
) -> None:
    """Add a domain to the runtime allowlist (survives until restart)."""
    from shieldy_dns.filter import add_to_allowlist
    add_to_allowlist(domain)
    console.print(f"[green]✓ Allowlisted:[/green] {domain}")
    console.print("[dim]Note: takes effect immediately but resets on restart. "
                  "Add to lists/custom.txt for permanent allowlisting.[/dim]")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
