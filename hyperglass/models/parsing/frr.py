"""Data Models for Parsing FRRouting JSON Response."""

# Standard Library
import typing as t
from datetime import datetime

# Third Party
from pydantic import ConfigDict, model_validator

# Project
from hyperglass.log import log
from hyperglass.models.data import BGPRouteTable

# Local
from ..main import HyperglassModel

FRRPeerType = t.Literal["internal", "external"]


def _alias_generator(field):
    components = field.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class _FRRBase(HyperglassModel):
    model_config = ConfigDict(alias_generator=_alias_generator, extra="ignore")


class FRRNextHop(_FRRBase):
    """FRR Next Hop Model."""

    ip: str
    afi: str
    metric: int
    accessible: bool
    used: bool


class FRRPeer(_FRRBase):
    """FRR Peer Model."""

    peer_id: str
    router_id: str
    type: FRRPeerType


class FRRPath(_FRRBase):
    """FRR Path Model."""

    aspath: t.List[int]
    aggregator_as: int
    aggregator_id: str
    med: int = 0
    localpref: int
    weight: int
    valid: bool
    last_update: int
    bestpath: bool
    community: t.List[str]
    nexthops: t.List[FRRNextHop]
    peer: FRRPeer

    @model_validator(pre=True)
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

    prefix: str
    paths: t.List[FRRPath] = []

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

        serialized = BGPRouteTable(
            vrf=vrf,
            count=len(routes),
            routes=routes,
            winning_weight="high",
        )

        log.bind(platform="frr", response=repr(serialized)).debug("Serialized response")
        return serialized
