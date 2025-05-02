"""Query & parse data from bgp.tools.

- See https://bgp.tools/credits for acknowledgements and licensing.
- See https://bgp.tools/kb/api for query documentation.
"""

# Standard Library
import re
import typing as t
import asyncio
from ipaddress import IPv4Address, IPv6Address, ip_address

# Project
from hyperglass.log import log
from hyperglass.state import use_state

DEFAULT_KEYS = ("asn", "ip", "prefix", "country", "rir", "allocated", "org")

CACHE_KEY = "hyperglass.external.bgptools"

TargetDetail = t.TypedDict(
    "TargetDetail",
    {"asn": str, "ip": str, "country": str, "rir": str, "allocated": str, "org": str},
)

TargetData = t.Dict[str, TargetDetail]


def default_ip_targets(*targets: str) -> t.Tuple[TargetData, t.Tuple[str, ...]]:
    """Construct a mapping of default data and other data that should be queried.

    Targets in the mapping don't need to be queried and already have default values. Targets in the
    query tuple should be queried.
    """
    default_data = {}
    query = ()
    for target in targets:
        detail: TargetDetail = {k: "None" for k in DEFAULT_KEYS}
        try:
            valid: t.Union[IPv4Address, IPv6Address] = ip_address(target)

            checks = (
                (valid.version == 6 and valid.is_site_local, "Site Local Address"),
                (valid.is_loopback, "Loopback Address"),
                (valid.is_multicast, "Multicast Address"),
                (valid.is_link_local, "Link Local Address"),
                (valid.is_private, "Private Address"),
            )
            for exp, rir in checks:
                if exp is True:
                    detail["rir"] = rir
                    break

            should_query = any((valid.is_global, valid.is_unspecified, valid.is_reserved))

            if not should_query:
                detail["ip"] = str(target)
                default_data[str(target)] = detail
            elif should_query:
                query += (str(target),)

        except ValueError:
            pass

    return default_data, query


def parse_whois(output: str, targets: t.List[str]) -> TargetDetail:
    """Parse raw whois output from bgp.tools.

    Sample output:
    AS    | IP      | BGP Prefix | CC | Registry | Allocated  | AS Name
    13335 | 1.1.1.1 | 1.1.1.0/24 | US | ARIN     | 2010-07-14 | Cloudflare, Inc.
    """

    def lines(raw):
        """Generate clean string values for each column."""
        for r in (r for r in raw.split("\n") if r):
            fields = (re.sub(r"(\n|\r)", "", field).strip(" ") for field in r.split("|"))
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
    log.bind(data=data).debug("Parsed bgp.tools data")
    return data


async def run_whois(targets: t.List[str]) -> str:
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


async def network_info(*targets: str) -> TargetData:
    """Get ASN, Containing Prefix, and other info about an internet resource."""

    default_data, query_targets = default_ip_targets(*targets)

    cache = use_state("cache")

    # Set default data structure.
    query_data = {t: {k: "" for k in DEFAULT_KEYS} for t in query_targets}

    # Get all cached bgp.tools data.
    cached = cache.get_map(CACHE_KEY) or {}

    # Try to use cached data for each of the items in the list of
    # resources.
    for target in (target for target in query_targets if target in cached):
        # Reassign the cached network info to the matching resource.
        query_data[target] = cached[target]
        log.bind(target=target).debug("Using cached network info")

    # Remove cached items from the resource list so they're not queried.
    targets = [t for t in query_targets if t not in cached]

    try:
        if targets:
            whoisdata = await run_whois(targets)

            if whoisdata:
                # If the response is not empty, parse it.
                query_data.update(parse_whois(whoisdata, targets))

                # Cache the response
                for target in targets:
                    cache.set_map_item(CACHE_KEY, target, query_data[target])
                    log.bind(target=t).debug("Cached network info")

    except Exception as err:
        log.error(err)

    return {**default_data, **query_data}


def network_info_sync(*targets: str) -> TargetData:
    """Get ASN, Containing Prefix, and other info about an internet resource."""
    return asyncio.run(network_info(*targets))
