"""Device-Agnostic Parsed Response Data Model."""

# Standard Library
import re
from typing import List

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, constr, validator

# Project
from hyperglass.models import HyperglassModel
from hyperglass.configuration import params
from hyperglass.external.rpki import rpki_state

WinningWeight = constr(regex=r"(low|high)")


class ParsedRouteEntry(HyperglassModel):
    """Per-Route Response Model."""

    prefix: StrictStr
    active: StrictBool
    age: StrictInt
    weight: StrictInt
    med: StrictInt
    local_preference: StrictInt
    as_path: List[StrictInt]
    communities: List[StrictStr]
    next_hop: StrictStr
    source_as: StrictInt
    source_rid: StrictStr
    peer_rid: StrictStr
    rpki_state: StrictInt

    @validator("communities")
    def validate_communities(cls, value):
        """Filter returned communities against configured policy.

        Actions:
            permit: only permit matches
            deny: only deny matches
        """

        def _permit(comm):
            """Only allow matching patterns."""
            valid = False
            for pattern in params.structured.communities.items:
                if re.match(pattern, comm):
                    valid = True
                    break
            return valid

        def _deny(comm):
            """Allow any except matching patterns."""
            valid = True
            for pattern in params.structured.communities.items:
                if re.match(pattern, comm):
                    valid = False
                    break
            return valid

        func_map = {"permit": _permit, "deny": _deny}
        func = func_map[params.structured.communities.mode]

        return [c for c in value if func(c)]

    @validator("rpki_state")
    def validate_rpki_state(cls, value, values):
        """If external RPKI validation is enabled, get validation state."""

        if params.structured.rpki.mode == "router":
            # If router validation is enabled, return the value as-is.
            return value

        elif params.structured.rpki.mode == "external":
            # If external validation is enabled, validate the prefix
            # & asn with Cloudflare's RPKI API.
            as_path = values["as_path"]

            if len(as_path) == 0:
                # If the AS_PATH length is 0, i.e. for an internal route,
                # return RPKI Unknown state.
                return 3
            else:
                # Get last ASN in path
                asn = as_path[-1]

            return rpki_state(prefix=values["prefix"], asn=asn)
        else:
            return value


class ParsedRoutes(HyperglassModel):
    """Parsed Response Model."""

    vrf: StrictStr
    count: StrictInt = 0
    routes: List[ParsedRouteEntry]
    winning_weight: WinningWeight
