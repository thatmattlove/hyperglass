"""Parser for Huawei VRP."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import ConfigDict, field_validator, model_validator

# Project
from hyperglass.log import log
from hyperglass.models.data.bgp_route import BGPRoute, BGPRouteTable

# Local
from ..main import HyperglassModel

RPKI_STATE_MAP = {
    "invalid": 0,
    "valid": 1,
    "unknown": 2,
    "unverified": 3,
}


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix from text if it exists."""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


class HuaweiBase(HyperglassModel, extra="ignore"):
    """Base Huawei model."""

    def __init__(self, **kwargs: t.Any) -> None:
        """Initialize Huawei model."""
        super().__init__(**kwargs)


class HuaweiPaths(HuaweiBase):
    """BGP paths information."""

    available: int = 0
    best: int = 0
    select: int = 0
    best_external: int = 0
    add_path: int = 0


class HuaweiRouteEntry(HuaweiBase):
    """Parse Huawei route entry data."""

    model_config = ConfigDict(validate_assignment=False)

    prefix: str
    from_addr: str = ""
    duration: int = 0
    direct_out_interface: str = ""
    original_next_hop: str = ""
    relay_ip_next_hop: str = ""
    relay_ip_out_interface: str = ""
    qos: str = ""
    communities: t.List[str] = []
    large_communities: t.List[str] = []
    ext_communities: t.List[str] = []
    as_path: t.List[int] = []
    origin: str = ""
    metric: int = 0  # MED
    local_preference: int = 100
    preference_value: int = 0
    is_valid: bool = False
    is_external: bool = False
    is_backup: bool = False
    is_best: bool = False
    is_selected: bool = False
    preference: int = 0

    @property
    def next_hop(self) -> str:
        """Get next hop (original or relay IP)."""
        return self.original_next_hop or self.relay_ip_next_hop

    @property
    def age(self) -> str:
        """Get age as string."""
        return str(self.duration)

    @property
    def weight(self) -> int:
        """Get weight (preference)."""
        return self.preference

    @property
    def med(self) -> int:
        """Get MED (metric)."""
        return self.metric

    @property
    def active(self) -> bool:
        """Check if route is active (best or selected)."""
        return self.is_best or self.is_selected

    @property
    def all_communities(self) -> t.List[str]:
        """Get all communities combined."""
        return self.communities + self.large_communities + self.ext_communities

    @property
    def source_as(self) -> int:
        """Get source AS from AS path."""
        return self.as_path[-1] if self.as_path else 0

    @property
    def source_rid(self) -> str:
        """Get source router ID."""
        return ""

    @property
    def peer_rid(self) -> str:
        """Get peer router ID."""
        return self.from_addr


def _extract_paths(line: str) -> HuaweiPaths:
    """Extract paths information from line like 'Paths: 3 available, 1 best, 1 select, 0 best-external, 0 add-path'."""
    paths_data = {
        "available": 0,
        "best": 0,
        "select": 0,
        "best_external": 0,
        "add_path": 0,
    }

    try:
        values = remove_prefix(line.strip(), "Paths:").strip().split(",")
        for value in values:
            parts = value.strip().split(" ")
            if len(parts) >= 2:
                count = int(parts[0])
                name = parts[1].replace("-", "_")  # Convert best-external to best_external
                if name in paths_data:
                    paths_data[name] = count
    except (ValueError, IndexError):
        log.warning(f"Failed to parse paths line: {line}")

    return HuaweiPaths(**paths_data)


def _extract_route_entries(lines: t.List[str]) -> t.List[HuaweiRouteEntry]:
    """Extract route entries from lines."""
    routes = []

    # Split lines into route blocks using empty lines as separators
    size = len(lines)
    idx_list = [idx + 1 for idx, val in enumerate(lines) if val.strip() == ""]
    entries = (
        [
            lines[i:j]
            for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))
        ]
        if idx_list
        else [lines]
    )

    for route_entry in entries:
        if not route_entry:
            continue

        # Initialize route data
        route_data = {
            "prefix": "",
            "from_addr": "",
            "duration": 0,
            "direct_out_interface": "",
            "original_next_hop": "",
            "relay_ip_next_hop": "",
            "relay_ip_out_interface": "",
            "qos": "",
            "communities": [],
            "large_communities": [],
            "ext_communities": [],
            "as_path": [],
            "origin": "",
            "metric": 0,
            "local_preference": 100,
            "preference_value": 0,
            "is_valid": False,
            "is_external": False,
            "is_backup": False,
            "is_best": False,
            "is_selected": False,
            "preference": 0,
        }

        for info in route_entry:
            info = info.strip()
            if not info:
                continue

            if info.startswith("BGP routing table entry information of"):
                route_data["prefix"] = remove_prefix(
                    info, "BGP routing table entry information of "
                ).rstrip(":")
            elif info.startswith("From:"):
                route_data["from_addr"] = remove_prefix(info, "From: ").split(" (")[0]
            elif info.startswith("Route Duration:"):
                duration_str = remove_prefix(info, "Route Duration: ")
                try:
                    # Parse format like "84d11h53m07s"
                    d_match = re.search(r"(\d+)d", duration_str)
                    h_match = re.search(r"(\d+)h", duration_str)
                    m_match = re.search(r"(\d+)m", duration_str)
                    s_match = re.search(r"(\d+)s", duration_str)

                    days = int(d_match.group(1)) if d_match else 0
                    hours = int(h_match.group(1)) if h_match else 0
                    minutes = int(m_match.group(1)) if m_match else 0
                    seconds = int(s_match.group(1)) if s_match else 0

                    route_data["duration"] = (
                        days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds
                    )
                except:
                    route_data["duration"] = 0
            elif info.startswith("Direct Out-interface:"):
                route_data["direct_out_interface"] = remove_prefix(info, "Direct Out-interface: ")
            elif info.startswith("Original nexthop:"):
                route_data["original_next_hop"] = remove_prefix(info, "Original nexthop: ")
            elif info.startswith("Relay IP Nexthop:"):
                route_data["relay_ip_next_hop"] = remove_prefix(info, "Relay IP Nexthop: ")
            elif info.startswith("Relay IP Out-Interface:"):
                route_data["relay_ip_out_interface"] = remove_prefix(
                    info, "Relay IP Out-Interface: "
                )
            elif info.startswith("Qos information :"):
                route_data["qos"] = remove_prefix(info, "Qos information : ")
            elif info.startswith("Community:"):
                communities_str = remove_prefix(info, "Community: ")
                if communities_str and communities_str.lower() != "none":
                    communities = [
                        c.strip().replace("<", "").replace(">", "")
                        for c in communities_str.split(", ")
                    ]
                    route_data["communities"] = [c for c in communities if c]
            elif info.startswith("Large-Community:"):
                large_communities_str = remove_prefix(info, "Large-Community: ")
                if large_communities_str and large_communities_str.lower() != "none":
                    large_communities = [
                        c.strip().replace("<", "").replace(">", "")
                        for c in large_communities_str.split(", ")
                    ]
                    route_data["large_communities"] = [c for c in large_communities if c]
            elif info.startswith("Ext-Community:"):
                ext_communities_str = remove_prefix(info, "Ext-Community: ")
                if ext_communities_str and ext_communities_str.lower() != "none":
                    ext_communities = [
                        c.strip().replace("<", "").replace(">", "")
                        for c in ext_communities_str.split(", ")
                    ]
                    route_data["ext_communities"] = [c for c in ext_communities if c]
            elif info.startswith("AS-path"):
                values = info.split(",")
                for v in values:
                    v = v.strip()
                    if v.startswith("AS-path"):
                        as_path_str = remove_prefix(v, "AS-path ")
                        try:
                            route_data["as_path"] = [
                                int(a) for a in as_path_str.split() if a.isdigit()
                            ]
                        except ValueError:
                            route_data["as_path"] = []
                    elif v.startswith("origin"):
                        route_data["origin"] = remove_prefix(v, "origin ")
                    elif v.startswith("MED"):
                        try:
                            route_data["metric"] = int(remove_prefix(v, "MED "))
                        except ValueError:
                            route_data["metric"] = 0
                    elif v.startswith("localpref"):
                        try:
                            route_data["local_preference"] = int(remove_prefix(v, "localpref "))
                        except ValueError:
                            route_data["local_preference"] = 100
                    elif v.startswith("pref-val"):
                        try:
                            route_data["preference_value"] = int(remove_prefix(v, "pref-val "))
                        except ValueError:
                            route_data["preference_value"] = 0
                    elif v.startswith("pre "):
                        try:
                            route_data["preference"] = int(remove_prefix(v, "pre "))
                        except ValueError:
                            route_data["preference"] = 0
                    elif v.strip() == "valid":
                        route_data["is_valid"] = True
                    elif v.strip() == "external":
                        route_data["is_external"] = True
                    elif v.strip() == "backup":
                        route_data["is_backup"] = True
                    elif v.strip() == "best":
                        route_data["is_best"] = True
                    elif v.strip() == "select":
                        route_data["is_selected"] = True

        # Only add route if we have a valid prefix
        if route_data["prefix"]:
            try:
                route = HuaweiRouteEntry(**route_data)
                routes.append(route)
            except Exception as e:
                log.warning(
                    f'Failed to create route entry for prefix {{route_data.get("prefix", "unknown")}}: {{e}}'
                )
                continue

    return routes


class HuaweiBGPRouteTable(BGPRouteTable):
    """Canonical Huawei BGP Route Table."""

    # No custom __init__ needed; inherit from BGPRouteTable (which should be a Pydantic model)


class HuaweiBGPTable(HuaweiBase):
    """Validation model for Huawei BGP table data."""

    local_router_id: str = ""
    local_as_number: int = 0
    paths: HuaweiPaths = HuaweiPaths()
    routes: t.List[HuaweiRouteEntry] = []

    @classmethod
    def parse_text(cls, text: str) -> "HuaweiBGPTable":
        """Parse Huawei BGP text output."""
        _log = log.bind(parser="HuaweiBGPTable")

        instance = cls()

        lines = text.split("\n")

        # Extract general information
        for line in lines:
            if "BGP local router ID" in line:
                instance.local_router_id = remove_prefix(line, "BGP local router ID : ").strip()
            elif "Local AS number" in line:
                try:
                    instance.local_as_number = int(
                        remove_prefix(line, "Local AS number : ").strip()
                    )
                except ValueError:
                    instance.local_as_number = 0
            elif line.strip().startswith("Paths:"):
                instance.paths = _extract_paths(line)

        # Extract route entries
        instance.routes = _extract_route_entries(lines)

        _log.debug(f"Parsed {len(instance.routes)} Huawei routes")
        return instance

    def bgp_table(self) -> BGPRouteTable:
        """Convert to standard BGP table format."""
        routes = []

        for route in self.routes:
            route_data = {
                "prefix": route.prefix,
                "active": route.active,
                "age": route.age,
                "weight": route.weight,
                "med": route.med,
                "local_preference": route.local_preference,
                "as_path": route.as_path,
                "communities": route.all_communities,
                "next_hop": route.next_hop,
                "source_as": route.source_as,
                "source_rid": route.source_rid,
                "peer_rid": route.peer_rid,
                "rpki_state": (
                    RPKI_STATE_MAP.get("unknown") if route.is_valid else RPKI_STATE_MAP.get("valid")
                ),
            }
            routes.append(BGPRoute(**route_data))

        return HuaweiBGPRouteTable(
            vrf="default",
            count=len(routes),
            routes=routes,
            winning_weight="high",
        )
