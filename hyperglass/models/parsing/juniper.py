"""Data Models for Parsing Juniper XML Response."""

# Standard Library
from typing import Any, Dict, List

# Third Party
from pydantic import validator, root_validator
from pydantic.types import StrictInt, StrictStr, StrictBool

# Project
from hyperglass.log import log
from hyperglass.util import deep_convert_keys
from hyperglass.models.data.bgp_route import BGPRouteTable

# Local
from ..main import HyperglassModel

RPKI_STATE_MAP = {
    "invalid": 0,
    "valid": 1,
    "unknown": 2,
    "unverified": 3,
}


class JuniperBase(HyperglassModel, extra="ignore"):
    """Base Juniper model."""

    def __init__(self, **kwargs: Any) -> None:
        """Convert all `-` keys to `_`.

        Default camelCase alias generator will still be used.
        """
        rebuilt = deep_convert_keys(kwargs, lambda k: k.replace("-", "_"))
        super().__init__(**rebuilt)


class JuniperRouteTableEntry(JuniperBase):
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
    communities: List[StrictStr] = None

    @root_validator(pre=True)
    def validate_optional_flags(cls, values):
        """Flatten & rename keys prior to validation."""
        next_hops = []
        nh = None

        # Handle Juniper's 'Router' Next Hop Type
        if "nh" in values:
            nh = values.pop("nh")

        # Handle Juniper's 'Indirect' Next Hop Type
        if "protocol_nh" in values:
            nh = values.pop("protocol_nh")

        # Force the next hops to be a list
        if isinstance(nh, Dict):
            nh = [nh]

        if nh is not None:
            next_hops.extend(nh)

        # Extract the 'to:' value from the next-hop
        selected_next_hop = ""
        for hop in next_hops:
            if "selected_next_hop" in hop:
                selected_next_hop = hop.get("to", "")
                break
            if hop.get("to") is not None:
                selected_next_hop = hop["to"]
                break

        values["next_hop"] = selected_next_hop

        _path_attr = values.get("bgp_path_attributes", {})
        _path_attr_agg = _path_attr.get("attr_aggregator", {}).get("attr_value", {})
        values["as_path"] = _path_attr.get("attr_as_path_effective", {}).get("attr_value", "")
        values["source_as"] = _path_attr_agg.get("aggr_as_number", 0)
        values["source_rid"] = _path_attr_agg.get("aggr_router_id", "")
        values["peer_rid"] = values.get("peer_id", "")

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
            except ValueError as err:
                raise ValueError(f"Age field is in an unexpected format. Got: {value}") from err
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
        if value is not None:
            flat = value.get("community", [])
        else:
            flat = []
        return flat


class JuniperRouteTable(JuniperBase):
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


class JuniperBGPTable(JuniperBase):
    """Validation model for route-table data."""

    table_name: StrictStr
    destination_count: int
    total_route_count: int
    active_route_count: int
    hidden_route_count: int
    rt: List[JuniperRouteTable]

    def bgp_table(self: "JuniperBGPTable") -> "BGPRouteTable":
        """Convert the Juniper-specific fields to standard parsed data model."""
        vrf_parts = self.table_name.split(".")
        if len(vrf_parts) == 2:
            vrf = "default"
        else:
            vrf = vrf_parts[0]

        routes = []
        count = 0
        for table in self.rt:
            count += table.rt_entry_count
            prefix = "/".join(str(i) for i in (table.rt_destination, table.rt_prefix_length))
            for route in table.rt_entry:
                routes.append(
                    {
                        "prefix": prefix,
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

        serialized = BGPRouteTable(vrf=vrf, count=count, routes=routes, winning_weight="low")

        log.debug("Serialized Juniper response: {}", repr(serialized))
        return serialized
