"""Data Models for Parsing FRRouting JSON Response."""

# Standard Library
from typing import List
from datetime import datetime

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, constr, root_validator

# Project
from hyperglass.log import log
from hyperglass.models import HyperglassModel
from hyperglass.parsing.models.serialized import ParsedRoutes

FRRPeerType = constr(regex=r"(internal|external)")


def _alias_generator(field):
    components = field.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class _FRRBase(HyperglassModel):
    class Config:
        alias_generator = _alias_generator
        extra = "ignore"


class FRRNextHop(_FRRBase):
    """FRR Next Hop Model."""

    ip: StrictStr
    afi: StrictStr
    metric: StrictInt
    accessible: StrictBool
    used: StrictBool


class FRRPeer(_FRRBase):
    """FRR Peer Model."""

    peer_id: StrictStr
    router_id: StrictStr
    type: FRRPeerType


class FRRPath(_FRRBase):
    """FRR Path Model."""

    aspath: List[StrictInt]
    aggregator_as: StrictInt
    aggregator_id: StrictStr
    med: StrictInt = 0
    localpref: StrictInt
    weight: StrictInt
    valid: StrictBool
    last_update: StrictInt
    bestpath: StrictBool
    community: List[StrictStr]
    nexthops: List[FRRNextHop]
    peer: FRRPeer

    @root_validator(pre=True)
    def validate_path(cls, values):
        """Extract meaningful data from FRR response."""
        new = values.copy()
        new["aspath"] = values["aspath"]["segments"][0]["list"]
        new["community"] = values["community"]["list"]
        new["lastUpdate"] = values["lastUpdate"]["epoch"]
        bestpath = values.get("bestpath", {})
        new["bestpath"] = bestpath.get("overall", False)
        return new


class FRRRoute(_FRRBase):
    """FRR Route Model."""

    prefix: StrictStr
    paths: List[FRRPath] = []

    def serialize(self):
        """Convert the FRR-specific fields to standard parsed data model."""

        # TODO: somehow, get the actual VRF
        vrf = "default"

        routes = []
        for route in self.paths:
            now = datetime.utcnow().timestamp()
            then = datetime.utcfromtimestamp(route.last_update).timestamp()
            age = int(now - then)
            routes.append(
                {
                    "prefix": self.prefix,
                    "active": route.bestpath,
                    "age": age,
                    "weight": route.weight,
                    "med": route.med,
                    "local_preference": route.localpref,
                    "as_path": route.aspath,
                    "communities": route.community,
                    "next_hop": route.nexthops[0].ip,
                    "source_as": route.aggregator_as,
                    "source_rid": route.aggregator_id,
                    "peer_rid": route.peer.peer_id,
                    # TODO: somehow, get the actual RPKI state
                    "rpki_state": 3,
                }
            )

        serialized = ParsedRoutes(
            vrf=vrf, count=len(routes), routes=routes, winning_weight="high",
        )

        log.info("Serialized FRR response: {}", serialized)
        return serialized
