"""Data Models for Parsing Arista JSON Response."""

# Standard Library
from typing import Dict, List, Optional
from datetime import datetime

# Project
from hyperglass.log import log

# Local
from ..main import HyperglassModel
from .serialized import ParsedRoutes

RPKI_STATE_MAP = {
    "invalid": 0,
    "valid": 1,
    "notFound": 2,
    "notValidated": 3,
}

WINNING_WEIGHT = "high"


def _alias_generator(field: str) -> str:
    caps = "".join(x for x in field.title() if x.isalnum())
    return caps[0].lower() + caps[1:]


class _AristaBase(HyperglassModel):
    """Base Model for Arista validation."""

    class Config:
        extra = "ignore"
        alias_generator = _alias_generator


class AristaAsPathEntry(_AristaBase):
    """Validation model for Arista asPathEntry."""

    as_path_type: str = "External"
    as_path: str = ""


class AristaPeerEntry(_AristaBase):
    """Validation model for Arista peerEntry."""

    peer_router_id: str
    peer_addr: str


class AristaRouteType(_AristaBase):
    """Validation model for Arista routeType."""

    origin: str
    suppressed: bool
    valid: bool
    active: bool
    origin_validity: Optional[str] = "notVerified"


class AristaRouteDetail(_AristaBase):
    """Validation for Arista routeDetail."""

    origin: str
    label_stack: List = []
    ext_community_list: List[str] = []
    ext_community_list_raw: List[str] = []
    community_list: List[str] = []
    large_community_list: List[str] = []


class AristaRoutePath(_AristaBase):
    """Validation model for Arista bgpRoutePaths."""

    as_path_entry: AristaAsPathEntry
    med: int
    local_preference: int
    weight: int
    peer_entry: AristaPeerEntry
    reason_not_bestpath: str
    timestamp: int = int(datetime.utcnow().timestamp())
    next_hop: str
    route_type: AristaRouteType
    route_detail: Optional[AristaRouteDetail]


class AristaRouteEntry(_AristaBase):
    """Validation model for Arista bgpRouteEntries."""

    total_paths: int = 0
    bgp_advertised_peer_groups: Dict = {}
    mask_length: int
    bgp_route_paths: List[AristaRoutePath] = []


class AristaRoute(_AristaBase):
    """Validation model for Arista bgpRouteEntries data."""

    router_id: str
    vrf: str
    bgp_route_entries: Dict[str, AristaRouteEntry]

    @staticmethod
    def _get_route_age(timestamp: int) -> int:
        now = datetime.utcnow()
        now_timestamp = int(now.timestamp())
        return now_timestamp - timestamp

    @staticmethod
    def _get_as_path(as_path: str) -> List[str]:
        return [int(p) for p in as_path.split() if p.isdecimal()]

    def serialize(self):
        """Convert the Arista-formatted fields to standard parsed data model."""
        routes = []
        count = 0
        for prefix, entries in self.bgp_route_entries.items():

            count += entries.total_paths

            for route in entries.bgp_route_paths:

                as_path = self._get_as_path(route.as_path_entry.as_path)
                rpki_state = RPKI_STATE_MAP.get(route.route_type.origin_validity, 3)

                # BGP AS Path and BGP Community queries do not include the routeDetail
                # block. Therefore, we must verify it exists before including its data.
                communities = []
                if route.route_detail is not None:
                    communities = route.route_detail.community_list

                routes.append(
                    {
                        "prefix": prefix,
                        "active": route.route_type.active,
                        "age": self._get_route_age(route.timestamp),
                        "weight": route.weight,
                        "med": route.med,
                        "local_preference": route.local_preference,
                        "as_path": as_path,
                        "communities": communities,
                        "next_hop": route.next_hop,
                        "source_as": as_path[0],
                        "source_rid": route.peer_entry.peer_router_id,
                        "peer_rid": route.peer_entry.peer_router_id,
                        "rpki_state": rpki_state,
                    }
                )

        serialized = ParsedRoutes(
            vrf=self.vrf, count=count, routes=routes, winning_weight=WINNING_WEIGHT,
        )

        log.debug("Serialized Arista response: {}", serialized)
        return serialized
