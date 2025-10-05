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
    def age(self) -> int:
        # MikroTik output does not provide route age, returning -1 to indicate unavailable.
        return -1

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
        # MikroTik output does not provide source RID, returning empty string.
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
                "rpki_state": route.rpki_state,
            }
            # Instantiate BGPRoute to trigger validation (including external RPKI)
            routes.append(BGPRoute(**route_data))
        return MikrotikBGPRouteTable(
            vrf="default",
            count=len(routes),
            routes=routes,
            winning_weight="low",
        )


class MikrotikTracerouteTable(MikrotikBase):
    """MikroTik Traceroute Table."""

    target: str
    source: str
    hops: t.List["MikrotikTracerouteHop"] = []
    max_hops: int = 30
    packet_size: int = 60

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> "MikrotikTracerouteTable":
        """Parse a cleaned MikroTik traceroute table.

        The input is expected to be a single, clean traceroute table that has already
        been processed by the garbage cleaner to remove paging artifacts and duplicates.

        Expected format:
        ADDRESS                          LOSS SENT    LAST     AVG    BEST   WORST STD-DEV STATUS
        197.157.67.233                     0%    3   0.4ms     0.2     0.1     0.4     0.1
                                         100%    3 timeout
        41.78.188.153                      0%    3 210.8ms   210.8   210.8   210.9       0
        """
        _log = log.bind(parser="MikrotikTracerouteTable")

        _log.debug(
            "Parsing cleaned MikroTik traceroute table",
            target=target,
            source=source,
            lines=len(text.splitlines()),
        )

        lines = text.strip().split("\n")
        hops = []
        hop_number = 1

        # Find the table header to start parsing from
        header_found = False
        data_start_index = 0

        for i, line in enumerate(lines):
            if "ADDRESS" in line and "LOSS" in line and "SENT" in line:
                header_found = True
                data_start_index = i + 1
                break

        if not header_found:
            _log.warning("No traceroute table header found in cleaned output")
            return MikrotikTracerouteTable(target=target, source=source, hops=[])

        # Parse data rows
        for i in range(data_start_index, len(lines)):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                continue

            # Stop at any remaining paging markers (shouldn't happen with cleaned input)
            if "-- [Q quit|C-z pause]" in line:
                break

            try:
                # Parse data line
                parts = line.split()
                if len(parts) < 3:
                    continue

                # Check if this is a timeout line (starts with percentage)
                if parts[0].endswith("%"):
                    # Timeout hop: "100% 3 timeout"
                    ip_address = None
                    loss_pct = int(parts[0].rstrip("%"))
                    sent_count = int(parts[1])
                    last_rtt = None
                    avg_rtt = None
                    best_rtt = None
                    worst_rtt = None
                else:
                    # Normal hop: "197.157.67.233 0% 3 0.4ms 0.2 0.1 0.4 0.1"
                    ip_address = parts[0]
                    if len(parts) < 7:
                        continue

                    loss_pct = int(parts[1].rstrip("%"))
                    sent_count = int(parts[2])

                    # Parse RTT values
                    def parse_rtt(rtt_str: str) -> t.Optional[float]:
                        if rtt_str in ("timeout", "-", "0ms", "*"):
                            return None
                        rtt_clean = re.sub(r"ms$", "", rtt_str)
                        try:
                            return float(rtt_clean)
                        except ValueError:
                            return None

                    last_rtt = parse_rtt(parts[3])
                    avg_rtt = parse_rtt(parts[4])
                    best_rtt = parse_rtt(parts[5])
                    worst_rtt = parse_rtt(parts[6])

                hop = MikrotikTracerouteHop(
                    hop_number=hop_number,
                    ip_address=ip_address,
                    hostname=None,  # MikroTik doesn't do reverse DNS by default
                    loss_pct=loss_pct,
                    sent_count=sent_count,
                    last_rtt=last_rtt,
                    avg_rtt=avg_rtt,
                    best_rtt=best_rtt,
                    worst_rtt=worst_rtt,
                )

                hops.append(hop)
                hop_number += 1

            except (ValueError, IndexError) as e:
                _log.debug("Failed to parse traceroute data line", line=line, error=str(e))
                continue

        result = MikrotikTracerouteTable(target=target, source=source, hops=hops)
        _log.info("Parsed cleaned traceroute table", hops=len(hops))
        return result

    def traceroute_result(self):
        """Convert to TracerouteResult format."""
        from hyperglass.models.data.traceroute import TracerouteResult, TracerouteHop
        from hyperglass.log import log

        _log = log.bind(parser="MikrotikTracerouteTable")

        converted_hops = []
        for hop in self.hops:
            # Handle truncated IP addresses
            ip_address = hop.ip_address
            display_ip = None

            if hop.ip_address and hop.ip_address.endswith("..."):
                # For truncated IPs, store for display but set ip_address to None for validation
                display_ip = hop.ip_address
                ip_address = None

            created_hop = TracerouteHop(
                hop_number=hop.hop_number,
                ip_address=ip_address,  # None for truncated IPs
                display_ip=display_ip,  # Truncated IP for display
                hostname=hop.hostname,
                # Set RTT values to ensure avg_rtt property returns MikroTik's AVG value
                # Since avg_rtt = (rtt1 + rtt2 + rtt3) / 3, we set all to the MikroTik AVG
                rtt1=hop.avg_rtt,  # Set to AVG so computed average is correct
                rtt2=hop.avg_rtt,  # Set to AVG so computed average is correct
                rtt3=hop.avg_rtt,  # Set to AVG so computed average is correct
                # MikroTik-specific statistics (preserve original values)
                loss_pct=hop.loss_pct,
                sent_count=hop.sent_count,
                last_rtt=hop.last_rtt,  # Preserve LAST value
                best_rtt=hop.best_rtt,  # Preserve BEST value
                worst_rtt=hop.worst_rtt,  # Preserve WORST value
                # BGP enrichment fields will be populated by enrichment plugin
                # For truncated IPs, these will remain None/empty
                asn=None,
                org=None,
                prefix=None,
                country=None,
                rir=None,
                allocated=None,
            )

            converted_hops.append(created_hop)

        return TracerouteResult(
            target=self.target,
            source=self.source,
            hops=converted_hops,
            max_hops=self.max_hops,
            packet_size=self.packet_size,
            raw_output=None,  # Will be set by the plugin
        )


class MikrotikTracerouteHop(MikrotikBase):
    """Individual MikroTik traceroute hop."""

    hop_number: int
    ip_address: t.Optional[str] = None
    hostname: t.Optional[str] = None

    # MikroTik-specific statistics
    loss_pct: t.Optional[int] = None
    sent_count: t.Optional[int] = None
    last_rtt: t.Optional[float] = None
    avg_rtt: t.Optional[float] = None
    best_rtt: t.Optional[float] = None
    worst_rtt: t.Optional[float] = None

    @property
    def is_timeout(self) -> bool:
        """Check if this hop is a timeout."""
        return self.ip_address is None or self.loss_pct == 100
