"""Device-Agnostic Parsed Response Data Model."""

# Standard Library
from typing import List

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, constr

# Project
from hyperglass.models import HyperglassModel


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


class ParsedRoutes(HyperglassModel):
    """Parsed Response Model."""

    vrf: StrictStr
    count: StrictInt = 0
    routes: List[ParsedRouteEntry]
    winning_weight: constr(regex=r"(low|high)")
