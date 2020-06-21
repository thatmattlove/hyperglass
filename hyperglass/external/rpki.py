"""Validate RPKI state via Cloudflare GraphQL API."""

# Project
from hyperglass.log import log
from hyperglass.external._base import BaseExternal

RPKI_STATE_MAP = {"Invalid": 0, "Valid": 1, "NotFound": 2, "DEFAULT": 3}
RPKI_NAME_MAP = {v: k for k, v in RPKI_STATE_MAP.items()}


def rpki_state(prefix, asn):
    """Get RPKI state and map to expected integer."""
    log.debug("Validating RPKI State for {p} via AS{a}", p=prefix, a=asn)

    state = 3
    query = 'query GetValidation {{ validation(prefix: "{prefix}", asn: {asn}) {{ state }} }}'.format(  # noqa: E501
        prefix=prefix, asn=asn
    )

    try:
        with BaseExternal(base_url="https://rpki.cloudflare.com") as client:
            response = client._post("/api/graphql", data={"query": query})
        validation_state = (
            response.get("data", {}).get("validation", {}).get("state", "DEFAULT")
        )
        state = RPKI_STATE_MAP[validation_state]
    except Exception:
        state = 3

    log.debug(
        "RPKI Validation State for {p} via AS{a} is {s}",
        p=prefix,
        a=asn,
        s=RPKI_NAME_MAP[state],
    )
    return state
