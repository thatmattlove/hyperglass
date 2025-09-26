"""Validate RPKI state via Cloudflare GraphQL API."""

# Standard Library
import typing as t
import requests

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.external._base import BaseExternal

if t.TYPE_CHECKING:
    from ipaddress import IPv4Address, IPv6Address

RPKI_STATE_MAP = {
    "Invalid": 0,
    "invalid": 0,
    "Valid": 1,
    "valid": 1,
    "NotFound": 2,
    "notfound": 2,
    "not_found": 2,
    "not-found": 2,
    "Unknown": 2,
    "unknown": 2,
    "DEFAULT": 3,
}
RPKI_NAME_MAP = {v: k for k, v in RPKI_STATE_MAP.items()}
CACHE_KEY = "hyperglass.external.rpki"


def rpki_state(
    prefix: t.Union["IPv4Address", "IPv6Address", str],
    asn: t.Union[int, str],
    backend: str = "cloudflare",
    rpki_server_url: str = "",
) -> int:
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
        try:
            if backend == "cloudflare":
                ql = 'query GetValidation {{ validation(prefix: "{}", asn: {}) {{ state }} }}'
                query = ql.format(prefix, asn)
                _log.bind(query=query).debug("Cloudflare RPKI GraphQL Query")
                with BaseExternal(base_url="https://rpki.cloudflare.com") as client:
                    response = client._post("/api/graphql", data={"query": query})
                validation_state = response["data"]["validation"]["state"]
            elif backend == "routinator":
                url = f"{rpki_server_url.rstrip('/')}/validity?asn={asn}&prefix={prefix}"
                _log.bind(url=url).debug("Routinator RPKI HTTP Query")
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                validation_state = data["validated_route"]["validity"]["state"]
            else:
                raise ValueError(f"Unknown RPKI backend: {backend}")

            state = RPKI_STATE_MAP.get(validation_state, 3)
            cache.set_map_item(CACHE_KEY, ro, state)
        except Exception as err:
            log.error(err)
            state = 3

    msg = "RPKI Validation State for {} via AS{} is {}".format(prefix, asn, RPKI_NAME_MAP[state])
    if cached is not None:
        msg += " [CACHED]"
    log.debug(msg)
    return state
