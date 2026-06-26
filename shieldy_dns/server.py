"""
dns/server.py — Shieldy's DNS listener

How it works:
  1. Client (your OS) sends a DNS query to 127.0.0.1:5353
  2. We receive the raw UDP packet and parse it with dnslib
  3. We extract the domain name being asked about
  4. We hand it to filter.py — blocked or allowed?
  5a. BLOCKED  → reply NXDOMAIN ("that domain doesn't exist") right here
  5b. ALLOWED  → hand it to upstream.py, get the real answer, forward it back

asyncio.DatagramProtocol is the standard Python way to handle UDP async.
Each query is handled in datagram_received() — no threads needed.
"""

import asyncio

import dnslib
from dnslib import DNSRecord, QTYPE, RCODE

import config
from shieldy_dns.filter import is_blocked
from shieldy_dns.upstream import resolve_upstream
from utils.logger import get_logger

log = get_logger(__name__)


class ShieldyProtocol(asyncio.DatagramProtocol):
    """
    asyncio UDP protocol — one instance handles ALL incoming DNS queries.
    datagram_received() fires every time a DNS packet arrives.
    """

    def __init__(self) -> None:
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        """Called once when the UDP socket is ready."""
        self.transport = transport
        log.info(f"[bold green]Shieldy 🛡️ listening on "
                 f"{config.DNS_HOST}:{config.DNS_PORT}[/bold green]")

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """
        Called for every incoming DNS query.
        addr = (client_ip, client_port) — almost always ('127.0.0.1', some_port)
        """
        # Parse the raw UDP bytes into a DNS request object
        try:
            request = DNSRecord.parse(data)
        except Exception as e:
            log.warning(f"Failed to parse DNS packet from {addr}: {e}")
            return

        # Extract the domain being queried, strip trailing dot
        # dnslib gives us "example.com." — we want "example.com"
        domain = str(request.q.qname).rstrip(".")
        qtype  = QTYPE[request.q.qtype]   # e.g. "A", "AAAA", "MX"

        log.debug(f"Query [{qtype}] {domain} from {addr[0]}")

        # Schedule the actual handling as an async task
        # We can't use await here directly (datagram_received isn't async)
        asyncio.ensure_future(
            self._handle(request, domain, qtype, addr)
        )

    async def _handle(
        self,
        request: DNSRecord,
        domain: str,
        qtype: str,
        addr: tuple[str, int],
    ) -> None:
        """
        Async handler — does the block/allow decision and sends the reply.
        Runs as a task so the server never blocks waiting for upstream.
        """
        blocked, category = is_blocked(domain)

        if blocked:
            reply = self._nxdomain(request)
            log.debug(f"BLOCKED [{category}] {domain}")
        else:
            reply = await resolve_upstream(request)
            if reply is None:
                # Upstream failed — return SERVFAIL so the OS knows to retry
                reply = request.reply()
                reply.header.rcode = RCODE.SERVFAIL
                log.warning(f"Upstream failed for {domain} — returning SERVFAIL")
            else:
                log.debug(f"ALLOWED {domain}")

        if self.transport:
            self.transport.sendto(reply.pack(), addr)

    @staticmethod
    def _nxdomain(request: DNSRecord) -> DNSRecord:
        """Build an NXDOMAIN reply — 'this domain does not exist'."""
        reply = request.reply()
        reply.header.rcode = RCODE.NXDOMAIN
        return reply


async def run_server() -> None:
    """
    Start the UDP DNS server. Call this from main.py with asyncio.run().

    Example:
        import asyncio
        from shieldy_dns.server import run_server
        asyncio.run(run_server())
    """
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        ShieldyProtocol,
        local_addr=(config.DNS_HOST, config.DNS_PORT),
    )

    log.info(f"DNS upstream: {config.DNS_UPSTREAM} / {config.DNS_UPSTREAM2}")
    log.info("Press Ctrl+C to stop")

    try:
        await asyncio.sleep(float("inf"))   # run forever
    except asyncio.CancelledError:
        pass
    finally:
        transport.close()
        log.info("Shieldy DNS server stopped")