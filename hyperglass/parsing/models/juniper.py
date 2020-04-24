"""Data Models for Parsing Juniper XML Response."""

# Standard Library
from typing import List

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, validator, root_validator

# Project
from hyperglass.log import log
from hyperglass.models import HyperglassModel
from hyperglass.parsing.models.serialized import ParsedRoutes

RPKI_STATE_MAP = {
    "invalid": 0,
    "valid": 1,
    "unknown": 2,
    "unverified": 3,
}


def _alias_generator(field):
    return field.replace("_", "-")


class _JuniperBase(HyperglassModel):
    class Config:
        alias_generator = _alias_generator
        extra = "ignore"


class JuniperRouteTableEntry(_JuniperBase):
    """Parse Juniper rt-entry data."""

    active_tag: StrictBool
    preference: int
    age: StrictInt
    local_preference: int
    metric: int = 0
    as_path: List[StrictInt] = []
    validation_state: StrictInt = 3
    next_hop: StrictStr
    peer_rid: StrictStr
    peer_as: int
    source_as: int
    source_rid: StrictStr
    communities: List[StrictStr]

    @root_validator(pre=True)
    def validate_optional_flags(cls, values):
        """Flatten & rename keys prior to validation."""
        values["next-hop"] = values.pop("nh").get("to", "")
        _path_attr = values.get("bgp-path-attributes", {})
        _path_attr_agg = _path_attr.get("attr-aggregator", {}).get("attr-value", {})
        values["as-path"] = _path_attr.get("attr-as-path-effective", {}).get(
            "attr-value", ""
        )
        values["source-as"] = _path_attr_agg.get("aggr-as-number", 0)
        values["source-rid"] = _path_attr_agg.get("aggr-router-id", "")
        values["peer-rid"] = values["peer-id"]
        return values

    @validator("validation_state", pre=True, always=True)
    def validate_rpki_state(cls, value):
        """Convert string RPKI state to standard integer mapping."""
        return RPKI_STATE_MAP.get(value, 3)

    @validator("active_tag", pre=True, always=True)
    def validate_active_tag(cls, value):
        """Convert active-tag from string/null to boolean."""
        if value == "*":
            value = True
        else:
            value = False
        return value

    @validator("age", pre=True, always=True)
    def validate_age(cls, value):
        """Get age as seconds."""
        if not isinstance(value, dict):
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Age field is in an unexpected format. Got: {value}")
        else:
            value = value.get("@junos:seconds", 0)
        return int(value)

    @validator("as_path", pre=True, always=True)
    def validate_as_path(cls, value):
        """Remove origin flags from AS_PATH."""
        disallowed = ("E", "I", "?")
        return [int(a) for a in value.split() if a not in disallowed]

    @validator("communities", pre=True, always=True)
    def validate_communities(cls, value):
        """Flatten community list."""
        return value.get("community", [])


class JuniperRouteTable(_JuniperBase):
    """Validation model for Juniper rt data."""

    rt_destination: StrictStr
    rt_prefix_length: int
    rt_entry_count: int
    rt_announced_count: int
    rt_entry: List[JuniperRouteTableEntry]

    @validator("rt_entry_count", pre=True, always=True)
    def validate_entry_count(cls, value):
        """Flatten & convert entry-count to integer."""
        return int(value.get("#text"))


class JuniperRoute(_JuniperBase):
    """Validation model for route-table data."""

    table_name: StrictStr
    destination_count: int
    total_route_count: int
    active_route_count: int
    hidden_route_count: int
    rt: JuniperRouteTable

    def serialize(self):
        """Convert the Juniper-specific fields to standard parsed data model."""
        vrf_parts = self.table_name.split(".")
        if len(vrf_parts) == 2:
            vrf = "default"
        else:
            vrf = vrf_parts[0]

        prefix = "/".join(
            str(i) for i in (self.rt.rt_destination, self.rt.rt_prefix_length)
        )

        structure = {
            "vrf": vrf,
            "prefix": prefix,
            "count": self.rt.rt_entry_count,
            "winning_weight": "low",
        }

        routes = []
        for route in self.rt.rt_entry:
            routes.append(
                {
                    "active": route.active_tag,
                    "age": route.age,
                    "weight": route.preference,
                    "med": route.metric,
                    "local_preference": route.local_preference,
                    "as_path": route.as_path,
                    "communities": route.communities,
                    "next_hop": route.next_hop,
                    "source_as": route.source_as,
                    "source_rid": route.source_rid,
                    "peer_rid": route.peer_rid,
                    "rpki_state": route.validation_state,
                }
            )

        serialized = ParsedRoutes(routes=routes, **structure)

        log.info("Serialized Juniper response: {}", serialized)
        return serialized
