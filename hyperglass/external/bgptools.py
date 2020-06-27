"""Query & parse data from bgp.tools."""

# Standard Library
import re
import socket
import asyncio

# Project
from hyperglass.log import log

REPLACE_KEYS = {
    "AS": "asn",
    "IP": "ip",
    "BGP Prefix": "prefix",
    "CC": "country",
    "Registry": "rir",
    "Allocated": "allocated",
    "AS Name": "org",
}


def parse_whois(output: str):
    """Parse raw whois output from bgp.tools.

    Sample output:
    AS      | IP               | BGP Prefix          | CC | Registry | Allocated  | AS Name # noqa: E501
    13335   | 1.1.1.1          | 1.1.1.0/24          | US | ARIN     | 2010-07-14 | Cloudflare, Inc.
    """

    # Each new line is a row.
    rawlines = output.split("\n")

    lines = ()
    for rawline in rawlines:

        # Split each row into fields, separated by a pipe.
        line = ()
        rawfields = rawline.split("|")

        for rawfield in rawfields:

            # Remove newline and leading/trailing whitespaces.
            field = re.sub(r"(\n|\r)", "", rawfield).strip(" ")
            line += (field,)

        lines += (line,)

    headers = lines[0]
    row = lines[1]
    data = {}

    for i, header in enumerate(headers):
        # Try to replace bgp.tools key names with easier to parse key names
        key = REPLACE_KEYS.get(header, header)
        data.update({key: row[i]})

    log.debug("Parsed bgp.tools data: {}", data)
    return data


async def run_whois(resource: str):
    """Open raw socket to bgp.tools and execute query."""

    # Open the socket to bgp.tools
    log.debug("Opening connection to bgp.tools")
    reader, writer = await asyncio.open_connection("bgp.tools", port=43)

    # Send the query
    writer.write(str(resource).encode())
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


def run_whois_sync(resource: str):
    """Open raw socket to bgp.tools and execute query."""

    # Open the socket to bgp.tools
    log.debug("Opening connection to bgp.tools")
    sock = socket.socket()
    sock.connect(("bgp.tools", 43))
    sock.send(f"{resource}\n".encode())

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


async def network_info(resource: str):
    """Get ASN, Containing Prefix, and other info about an internet resource."""

    data = {v: "" for v in REPLACE_KEYS.values()}

    try:

        if resource is not None:
            whoisdata = await run_whois(resource)

            if whoisdata:
                # If the response is not empty, parse it.
                data = parse_whois(whoisdata)

    except Exception as err:
        log.error(str(err))

    return data


def network_info_sync(resource: str):
    """Get ASN, Containing Prefix, and other info about an internet resource."""

    data = {v: "" for v in REPLACE_KEYS.values()}

    try:

        if resource is not None:
            whoisdata = run_whois_sync(resource)

            if whoisdata:
                # If the response is not empty, parse it.
                data = parse_whois(whoisdata)

    except Exception as err:
        log.error(str(err))

    return data
