"""Validate RPKI state via Cloudflare GraphQL API."""

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.external._base import BaseExternal

RPKI_STATE_MAP = {"Invalid": 0, "Valid": 1, "NotFound": 2, "DEFAULT": 3}
RPKI_NAME_MAP = {v: k for k, v in RPKI_STATE_MAP.items()}
CACHE_KEY = "hyperglass.external.rpki"


def rpki_state(prefix, asn):
    """Get RPKI state and map to expected integer."""
    log.debug("Validating RPKI State for {p} via AS{a}", p=prefix, a=asn)

    (cache := use_state().redis)

    state = 3
    ro = f"{prefix}@{asn}"

    cached = cache.hget(CACHE_KEY, ro)

    if cached is not None:
        state = cached
    else:

        ql = 'query GetValidation {{ validation(prefix: "{}", asn: {}) {{ state }} }}'
        query = ql.format(prefix, asn)

        try:
            with BaseExternal(base_url="https://rpki.cloudflare.com") as client:
                response = client._post("/api/graphql", data={"query": query})
            validation_state = (
                response.get("data", {}).get("validation", {}).get("state", "DEFAULT")
            )
            state = RPKI_STATE_MAP[validation_state]
            cache.hset(CACHE_KEY, ro, state)
        except Exception as err:
            log.error(str(err))
            state = 3

    msg = "RPKI Validation State for {} via AS{} is {}".format(prefix, asn, RPKI_NAME_MAP[state])
    if cached is not None:
        msg += " [CACHED]"

    log.debug(msg)
    return state
