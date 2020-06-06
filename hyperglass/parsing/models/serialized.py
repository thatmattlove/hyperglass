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
        valid = []
        for community in value:
            for pattern in params.structured.communities.items:
                # For each community in the response, compare it to the
                # configured list of 'items' under
                # params.structured.communities.items.
                if re.match(pattern, community):
                    # If there is a match and the action is 'permit',
                    # allow the community to be shown.
                    if params.structured.communities.mode == "permit":
                        valid.append(community)
                        break
                    # If the action is permit and there is no match,
                    # this means the user doesn't want to show the
                    # community.
                else:
                    # If there is not a match and the action is 'deny',
                    # allow the community to be shown.
                    if params.structured.communities.mode == "deny":
                        valid.append(community)
                        break
                    # If the action is 'deny' and there is a match,
                    # this means the user doesn't want to show the
                    # community.
        return valid

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
    winning_weight: constr(regex=r"(low|high)")
