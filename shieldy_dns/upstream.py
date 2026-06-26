"""
dns/upstream.py — forward allowed DNS queries to a real upstream resolver

When a domain is NOT blocked, we need to get the real answer.
We send the original query to 1.1.1.1 (Cloudflare) or 9.9.9.9 (Quad9),
wait for the reply, and hand it back to server.py to forward to the client.

This uses a raw UDP socket wrapped in asyncio — same protocol as the
incoming queries, just pointed outward at the upstream server.
"""

import asyncio
import socket

import config
import dnslib
from dnslib import DNSRecord
from utils.logger import get_logger

log = get_logger(__name__)


async def resolve_upstream(
    request: DNSRecord,
    upstream: str | None = None,
) -> DNSRecord | None:
    """
    Forward a DNS query to the upstream resolver and return the answer.

    Args:
        request:  The original DNSRecord from the client.
        upstream: Override the upstream IP (defaults to config.DNS_UPSTREAM).

    Returns:
        DNSRecord reply, or None if upstream timed out / errored.
    """
    upstream = upstream or config.DNS_UPSTREAM

    try:
        return await asyncio.wait_for(
            _send_udp(request.pack(), upstream),
            timeout=config.DNS_TIMEOUT,
        )
    except asyncio.TimeoutError:
        log.warning(
            f"Upstream {upstream} timed out — trying fallback {config.DNS_UPSTREAM2}"
        )
        # Try the fallback upstream once before giving up
        if upstream != config.DNS_UPSTREAM2:
            return await resolve_upstream(request, upstream=config.DNS_UPSTREAM2)
        log.error("Both upstreams timed out")
        return None
    except Exception as e:
        log.error(f"Upstream error ({upstream}): {e}")
        return None


async def _send_udp(data: bytes, upstream: str) -> DNSRecord | None:
    """
    Send raw DNS bytes over UDP to the upstream and await the reply.
    Uses asyncio's low-level socket API on a non-blocking socket.
    """
    loop = asyncio.get_running_loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    try:
        # Connect first — required before sock_sendall on UDP
        await loop.sock_connect(sock, (upstream, 53))
        await loop.sock_sendall(sock, data)

        # DNS responses are at most 512 bytes for plain UDP
        raw = await loop.sock_recv(sock, 512)
        return DNSRecord.parse(raw)

    finally:
        sock.close()
