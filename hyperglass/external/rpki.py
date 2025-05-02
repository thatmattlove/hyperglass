"""Validate RPKI state via Cloudflare GraphQL API."""

# Standard Library
import typing as t

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.external._base import BaseExternal

if t.TYPE_CHECKING:
    # Standard Library
    from ipaddress import IPv4Address, IPv6Address

RPKI_STATE_MAP = {"Invalid": 0, "Valid": 1, "NotFound": 2, "DEFAULT": 3}
RPKI_NAME_MAP = {v: k for k, v in RPKI_STATE_MAP.items()}
CACHE_KEY = "hyperglass.external.rpki"


def rpki_state(prefix: t.Union["IPv4Address", "IPv6Address", str], asn: t.Union[int, str]) -> int:
    """Get RPKI state and map to expected integer."""
    _log = log.bind(prefix=prefix, asn=asn)
    _log.debug("Validating RPKI State")

    cache = use_state("cache")

    state = 3
    ro = f"{prefix!s}@{asn!s}"

    cached = cache.get_map(CACHE_KEY, ro)

    if cached is not None:
        state = cached
    else:
        ql = 'query GetValidation {{ validation(prefix: "{}", asn: {}) {{ state }} }}'
        query = ql.format(prefix, asn)
        _log.bind(query=query).debug("Cloudflare RPKI GraphQL Query")
        try:
            with BaseExternal(base_url="https://rpki.cloudflare.com") as client:
                response = client._post("/api/graphql", data={"query": query})
            try:
                validation_state = response["data"]["validation"]["state"]
            except KeyError as missing:
                _log.error("Response from Cloudflare missing key '{}': {!r}", missing, response)
                validation_state = 3

            state = RPKI_STATE_MAP[validation_state]
            cache.set_map_item(CACHE_KEY, ro, state)
        except Exception as err:
            log.error(err)
            # Don't cache the state when an error produced it.
            state = 3

    msg = "RPKI Validation State for {} via AS{} is {}".format(prefix, asn, RPKI_NAME_MAP[state])
    if cached is not None:
        msg += " [CACHED]"

    log.debug(msg)
    return state
