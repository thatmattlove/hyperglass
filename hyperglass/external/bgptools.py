"""Query & parse data from bgp.tools.

- See https://bgp.tools/credits for acknowledgements and licensing.
- See https://bgp.tools/kb/api for query documentation.
"""

# Standard Library
import re
import socket
import asyncio
from typing import Dict, List

# Project
from hyperglass.log import log
from hyperglass.cache import SyncCache, AsyncCache
from hyperglass.configuration import REDIS_CONFIG, params

DEFAULT_KEYS = ("asn", "ip", "prefix", "country", "rir", "allocated", "org")

CACHE_KEY = "hyperglass.external.bgptools"


def parse_whois(output: str, targets: List[str]) -> Dict[str, str]:
    """Parse raw whois output from bgp.tools.

    Sample output:
    AS    | IP      | BGP Prefix | CC | Registry | Allocated  | AS Name
    13335 | 1.1.1.1 | 1.1.1.0/24 | US | ARIN     | 2010-07-14 | Cloudflare, Inc.
    """

    def lines(raw):
        """Generate clean string values for each column."""
        for r in (r for r in raw.split("\n") if r):
            fields = (
                re.sub(r"(\n|\r)", "", field).strip(" ") for field in r.split("|")
            )
            yield fields

    data = {}

    for line in lines(output):

        # Unpack each line's parsed values.
        asn, ip, prefix, country, rir, allocated, org = line

        # Match the line to the item in the list of resources to query.
        if ip in targets:
            i = targets.index(ip)
            data[targets[i]] = {
                "asn": asn,
                "ip": ip,
                "prefix": prefix,
                "country": country,
                "rir": rir,
                "allocated": allocated,
                "org": org,
            }

    log.debug("Parsed bgp.tools data: {}", data)
    return data


async def run_whois(targets: List[str]) -> str:
    """Open raw socket to bgp.tools and execute query."""

    # Construct bulk query
    query = "\n".join(("begin", *targets, "end\n")).encode()

    # Open the socket to bgp.tools
    log.debug("Opening connection to bgp.tools")
    reader, writer = await asyncio.open_connection("bgp.tools", port=43)

    # Send the query
    writer.write(query)
    if writer.can_write_eof():
        writer.write_eof()
    await writer.drain()

    # Read the response
    response = b""
    while True:
        data = await reader.read(128)
        if data:
            response += data
        else:
            log.debug("Closing connection to bgp.tools")
            writer.close()
            break

    return response.decode()


def run_whois_sync(targets: List[str]) -> str:
    """Open raw socket to bgp.tools and execute query."""

    # Construct bulk query
    query = "\n".join(("begin", *targets, "end\n")).encode()

    # Open the socket to bgp.tools
    log.debug("Opening connection to bgp.tools")
    sock = socket.socket()
    sock.connect(("bgp.tools", 43))
    sock.send(query)

    # Read the response
    response = b""
    while True:
        data = sock.recv(128)
        if data:
            response += data

        else:
            log.debug("Closing connection to bgp.tools")
            sock.shutdown(1)
            sock.close()
            break

    return response.decode()


async def network_info(*targets: str) -> Dict[str, Dict[str, str]]:
    """Get ASN, Containing Prefix, and other info about an internet resource."""

    targets = [str(t) for t in targets]
    cache = AsyncCache(db=params.cache.database, **REDIS_CONFIG)

    # Set default data structure.
    data = {t: {k: "" for k in DEFAULT_KEYS} for t in targets}

    # Get all cached bgp.tools data.
    cached = await cache.get_dict(CACHE_KEY)

    # Try to use cached data for each of the items in the list of
    # resources.
    for t in targets:

        if t in cached:
            # Reassign the cached network info to the matching resource.
            data[t] = cached[t]
            log.debug("Using cached network info for {}", t)

    # Remove cached items from the resource list so they're not queried.
    targets = [t for t in targets if t not in cached]

    try:
        if targets:
            whoisdata = await run_whois(targets)

            if whoisdata:
                # If the response is not empty, parse it.
                data.update(parse_whois(whoisdata, targets))

                # Cache the response
                for t in targets:
                    await cache.set_dict(CACHE_KEY, t, data[t])
                    log.debug("Cached network info for {}", t)

    except Exception as err:
        log.error(str(err))

    return data


def network_info_sync(*targets: str) -> Dict[str, Dict[str, str]]:
    """Get ASN, Containing Prefix, and other info about an internet resource."""

    targets = [str(t) for t in targets]
    cache = SyncCache(db=params.cache.database, **REDIS_CONFIG)

    # Set default data structure.
    data = {t: {k: "" for k in DEFAULT_KEYS} for t in targets}

    # Get all cached bgp.tools data.
    cached = cache.get_dict(CACHE_KEY)

    # Try to use cached data for each of the items in the list of
    # resources.
    for t in targets:

        if t in cached:
            # Reassign the cached network info to the matching resource.
            data[t] = cached[t]
            log.debug("Using cached network info for {}", t)

    # Remove cached items from the resource list so they're not queried.
    targets = [t for t in targets if t not in cached]

    try:
        if targets:
            whoisdata = run_whois_sync(targets)

            if whoisdata:
                # If the response is not empty, parse it.
                data.update(parse_whois(whoisdata, targets))

                # Cache the response
                for t in targets:
                    cache.set_dict(CACHE_KEY, t, data[t])
                    log.debug("Cached network info for {}", t)

    except Exception as err:
        log.error(str(err))

    return data
