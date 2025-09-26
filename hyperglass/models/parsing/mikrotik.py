"""Parser for MikroTik RouterOS (ROS v6/v7) – structured in Huawei style."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import ConfigDict

# Project
from hyperglass.log import log
from hyperglass.models.data.bgp_route import BGPRoute, BGPRouteTable  # Add BGPRoute import

# Local
from ..main import HyperglassModel

RPKI_STATE_MAP = {
    "invalid": 0,
    "valid": 1,
    "unknown": 2,
    "unverified": 3,
}


def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


# Regex to find key=value pairs. The key can contain dots and hyphens.
# The value can be quoted or a single word.
TOKEN_RE = re.compile(r'([a-zA-Z0-9_.-]+)=(".*?"|\S+)')

# Regex to find flags at the beginning of a line (e.g., "Ab   dst-address=...")
FLAGS_RE = re.compile(r"^\s*([DXIAcmsroivmyH\+b]+)\s+")


class MikrotikBase(HyperglassModel, extra="ignore"):
    def __init__(self, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)


class MikrotikPaths(MikrotikBase):
    available: int = 0
    best: int = 0
    select: int = 0
    best_external: int = 0
    add_path: int = 0


class MikrotikRouteEntry(MikrotikBase):
    """MikroTik Route Entry."""

    model_config = ConfigDict(validate_assignment=False)

    prefix: str
    gateway: str = ""
    distance: int = 0
    scope: int = 0
    target_scope: int = 0
    as_path: t.List[int] = []
    communities: t.List[str] = []
    large_communities: t.List[str] = []
    ext_communities: t.List[str] = []
    local_preference: int = 100
    metric: int = 0  # MED
    origin: str = ""
    is_active: bool = False
    is_best: bool = False
    is_valid: bool = False
    rpki_state: int = RPKI_STATE_MAP.get("unknown", 2)

    @property
    def next_hop(self) -> str:
        return self.gateway

    @property
    def age(self) -> str:
        # MikroTik output does not provide route age, returning 0 as a placeholder.
        return "0"

    @property
    def weight(self) -> int:
        return self.distance

    @property
    def med(self) -> int:
        return self.metric

    @property
    def active(self) -> bool:
        return self.is_active or self.is_best

    @property
    def all_communities(self) -> t.List[str]:
        return self.communities + self.large_communities + self.ext_communities

    @property
    def source_as(self) -> int:
        return self.as_path[-1] if self.as_path else 0

    @property
    def source_rid(self) -> str:
        return ""

    @property
    def peer_rid(self) -> str:
        return self.gateway


def _extract_paths(lines: t.List[str]) -> MikrotikPaths:
    """Simple count based on lines with dst/dst-address and 'A' flag."""
    available = 0
    best = 0
    for raw in lines:
        if ("dst-address=" in raw) or (" dst=" in f" {raw} "):
            available += 1
            m = FLAGS_RE.match(raw)
            if m and "A" in m.group(1):
                best += 1
    return MikrotikPaths(available=available, best=best, select=best)


def _process_kv(route: dict, key: str, val: str):
    _log = log.bind(parser="MikrotikBGPTable")
    """Process a key-value pair and update the route dictionary."""
    # Normalize quoted values
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]

    if key in ("dst-address", "dst"):
        route["prefix"] = val
    elif key in ("gateway", "nexthop"):
        # Extract only the IP from gateway (e.g., 168.254.0.2%vlan-2000)
        route["gateway"] = val.split("%")[0]
    elif key == "distance":
        route["distance"] = int(val) if val.isdigit() else route.get("distance", 0)
    elif key == "scope":
        route["scope"] = int(val) if val.isdigit() else route.get("scope", 0)
    elif key in ("target-scope", "target_scope"):
        route["target_scope"] = int(val) if val.isdigit() else route.get("target_scope", 0)

    # v7 keys (with dot)
    elif key in (".as-path", "as-path", "bgp-as-path"):
        if val and val.lower() != "none":
            # Find all numbers in the as-path string
            nums = re.findall(r"\b\d{1,10}\b", val)
            route["as_path"] = [int(n) for n in nums if 1 <= int(n) <= 4294967295]
    elif key in (".origin", "origin", "bgp-origin"):
        route["origin"] = val
    elif key in (".med", "med", "bgp-med"):
        route["metric"] = int(val) if val.isdigit() else 0
    elif key in (".local-pref", "local-pref", "bgp-local-pref"):
        route["local_preference"] = int(val) if val.isdigit() else 100
    elif key in (".communities", "communities", "bgp-communities"):
        if val and val.lower() != "none":
            route["communities"] = [c.strip() for c in val.split(",") if c.strip()]
    elif key in (".large-communities", "large-communities", "bgp-large-communities"):
        if val and val.lower() != "none":
            route["large_communities"] = [c.strip() for c in val.split(",") if c.strip()]
    elif key == "bgp-ext-communities":
        if val and val.lower() != "none":
            route["ext_communities"] = [c.strip() for c in val.split(",") if c.strip()]
    elif key == "rpki":
        # _log.debug(f"RPKI raw value: {val!r}")
        clean_val = val.strip().strip('"').lower()
        route["rpki_state"] = RPKI_STATE_MAP.get(clean_val, 2)


def _extract_route_entries(lines: t.List[str]) -> t.List[MikrotikRouteEntry]:
    """Extract route entries from a list of lines."""
    routes: t.List[MikrotikRouteEntry] = []
    current_route_lines = []

    for line in lines:
        stripped_line = line.strip()
        # A new route entry starts with flags or is a continuation line.
        # An empty line signifies the end of the previous block.
        if not stripped_line and current_route_lines:
            # Process the completed route block
            route_data = _parse_route_block(current_route_lines)
            if route_data:
                routes.append(route_data)
            current_route_lines = []
        elif stripped_line:
            # Check if this line is the start of a new entry
            if FLAGS_RE.match(stripped_line) and current_route_lines:
                route_data = _parse_route_block(current_route_lines)
                if route_data:
                    routes.append(route_data)
                current_route_lines = [stripped_line]
            else:
                current_route_lines.append(stripped_line)

    # Process any remaining lines
    if current_route_lines:
        route_data = _parse_route_block(current_route_lines)
        if route_data:
            routes.append(route_data)

    return routes


def _parse_route_block(block: t.List[str]) -> t.Optional[MikrotikRouteEntry]:
    """Parse a single route block and return a MikrotikRouteEntry."""
    if not block:
        return None

    full_block_text = " ".join(block)
    if "dst-address=" not in full_block_text and " dst=" not in f" {full_block_text} ":
        return None

    rd = {
        "prefix": "",
        "gateway": "",
        "distance": 20,
        "scope": 30,
        "target_scope": 10,
        "as_path": [],
        "communities": [],
        "large_communities": [],
        "ext_communities": [],
        "local_preference": 100,
        "metric": 0,
        "origin": "",
        "is_active": False,
        "is_best": False,
        "is_valid": False,
        "rpki_state": RPKI_STATE_MAP.get("unknown", 2),
    }

    # Check for 'A' (active) flag in the first line
    m = FLAGS_RE.match(block[0])
    if m and "A" in m.group(1):
        rd["is_active"] = True
        rd["is_best"] = True

    # Find all key=value tokens in the entire block
    for k, v in TOKEN_RE.findall(full_block_text):
        _process_kv(rd, k, v)

    if rd["prefix"]:
        try:
            return MikrotikRouteEntry(**rd)
        except Exception as e:
            log.warning(f"Failed to create MikroTik route entry ({rd.get('prefix','?')}: {e}")
    return None


class MikrotikBGPRouteTable(BGPRouteTable):
    """Canonical MikroTik BGP Route Table."""
    # No custom __init__ needed; inherit from BGPRouteTable (which should be a Pydantic model)


class MikrotikBGPTable(MikrotikBase):
    """MikroTik BGP Table in canonical format."""

    local_router_id: str = ""
    local_as_number: int = 0
    paths: MikrotikPaths = MikrotikPaths()
    routes: t.List[MikrotikRouteEntry] = []

    @classmethod
    def parse_text(cls, text: str) -> "MikrotikBGPTable":
        _log = log.bind(parser="MikrotikBGPTable")
        inst = cls()

        lines = text.splitlines()
        if not lines:
            return inst

        # Filter out command echoes and header lines
        lines = [ln for ln in lines if not ln.strip().startswith((">", "Flags:", "[", "#"))]

        inst.paths = _extract_paths(lines)
        inst.routes = _extract_route_entries(lines)

        _log.debug(f"Parsed {len(inst.routes)} MikroTik routes")
        return inst

    def bgp_table(self) -> BGPRouteTable:
        out = []
        for r in self.routes:
            route_dict = {
                "prefix": r.prefix,
                "active": r.active,
                "age": r.age,
                "weight": r.weight,
                "med": r.med,
                "local_preference": r.local_preference,
                "as_path": r.as_path,
                "communities": r.all_communities,
                "next_hop": r.next_hop,
                "source_as": r.source_as,
                "source_rid": r.source_rid,
                "peer_rid": r.peer_rid,
                "rpki_state": r.rpki_state,
            }
            # Instantiate BGPRoute to trigger validation (including external RPKI)
            out.append(BGPRoute(**route_dict))
        return MikrotikBGPRouteTable(
            vrf="default",
            count=len(out),
            routes=out,
            winning_weight="low",
        )
