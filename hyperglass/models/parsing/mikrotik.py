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
        """Parse MikroTik traceroute output.

        MikroTik shows multiple complete tables over time as it builds the traceroute:

        Columns: ADDRESS, LOSS, SENT, LAST, AVG, BEST, WORST, STD-DEV
        #  ADDRESS         LOSS  SENT  LAST    AVG   BEST  WORST  STD-DEV
        1  10.0.0.41         0%     1  0.5ms   0.5   0.5   0.5      0
        2  185.73.201.193    0%     1  0.4ms   0.4   0.4   0.4      0
        3  46.31.76.111      0%     1  0.5ms   0.5   0.5   0.5      0
        4                   0%     1  0ms
        -- [Q quit|C-z pause]
        Columns: ADDRESS, LOSS, SENT, LAST, AVG, BEST, WORST, STD-DEV
        #  ADDRESS         LOSS  SENT  LAST    AVG   BEST  WORST  STD-DEV
        1  10.0.0.41         0%     1  0.5ms   0.5   0.5   0.5      0
        2  185.73.201.193    0%     1  0.4ms   0.4   0.4   0.4      0
        ...more tables...

        We need to find the LAST/NEWEST table and use that as the final result.
        """
        _log = log.bind(parser="MikrotikTracerouteTable")

        # DEBUG: Log the raw input
        _log.debug(f"=== RAW MIKROTIK TRACEROUTE INPUT ===")
        _log.debug(f"Target: {target}, Source: {source}")
        _log.debug(f"Raw text length: {len(text)} characters")
        _log.debug(f"Raw text:\n{repr(text)}")
        _log.debug(f"=== END RAW INPUT ===")

        lines = text.strip().split("\n")
        _log.debug(f"Split into {len(lines)} lines")

        # DEBUG: Log each line with line numbers
        for i, line in enumerate(lines):
            _log.debug(f"Line {i:2d}: {repr(line)}")

        # Find all table starts - handle both formats:
        # Format 1: "Columns: ADDRESS, LOSS, SENT..." (newer format with hop numbers)
        # Format 2: "ADDRESS                          LOSS SENT..." (older format, no hop numbers)
        table_starts = []
        for i, line in enumerate(lines):
            if ("Columns:" in line and "ADDRESS" in line) or (
                "ADDRESS" in line
                and "LOSS" in line
                and "SENT" in line
                and not line.strip().startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9"))
            ):
                table_starts.append(i)
                _log.debug(f"Found table start at line {i}: {repr(line)}")

        if not table_starts:
            _log.warning("No traceroute table headers found in output")
            return MikrotikTracerouteTable(target=target, source=source, hops=[])

        # Take the LAST table (newest/final results)
        last_table_start = table_starts[-1]
        _log.debug(
            f"Found {len(table_starts)} tables, using the last one starting at line {last_table_start}"
        )

        # Determine format by checking the header line
        header_line = lines[last_table_start].strip()
        is_columnar_format = "Columns:" in header_line
        _log.debug(f"Header line: {repr(header_line)}")
        _log.debug(f"Is columnar format: {is_columnar_format}")

        # Parse only the last table
        hops = []
        in_data_section = False
        current_hop_number = 1  # Track the current hop number
        hop_counter = 1  # For old format without hop numbers

        # Start from the last table header
        for i in range(last_table_start, len(lines)):
            original_line = lines[i]  # Keep original line with whitespace
            line = original_line.strip()  # Stripped version for most processing

            # Skip empty lines
            if not line:
                _log.debug(f"Line {i}: EMPTY - skipping")
                continue

            # Skip the column header lines
            if (
                ("Columns:" in line)
                or ("ADDRESS" in line and "LOSS" in line and "SENT" in line)
                or line.startswith("#")
            ):
                in_data_section = True
                _log.debug(f"Line {i}: HEADER - entering data section: {repr(line)}")
                continue

            # Skip paging prompts
            if "-- [Q quit|C-z pause]" in line:
                _log.debug(f"Line {i}: PAGING PROMPT - breaking: {repr(line)}")
                break  # End of this table

            if in_data_section and line:
                _log.debug(f"Line {i}: PROCESSING DATA LINE: {repr(line)}")
                try:
                    # Define helper function for RTT parsing
                    def parse_rtt(rtt_str: str) -> t.Optional[float]:
                        if rtt_str in ("timeout", "-", "0ms"):
                            return None
                        # Remove 'ms' suffix and convert to float
                        rtt_clean = re.sub(r"ms$", "", rtt_str)
                        try:
                            return float(rtt_clean)
                        except ValueError:
                            return None

                    # Check if this is a timeout/continuation line (starts with whitespace, has % and numbers)
                    # Use original_line to check for leading whitespace
                    if (
                        (original_line.startswith(" ") or original_line.startswith("\t"))
                        and "%" in line
                        and ("timeout" in line or "0ms" in line)
                    ):
                        # This is a timeout/continuation hop
                        parts = line.split()
                        _log.debug(f"Line {i}: Timeout/continuation line, parts: {parts}")

                        if len(parts) >= 2 and parts[0].endswith("%"):
                            ip_address = None
                            loss_pct = int(parts[0].rstrip("%"))
                            sent_count = int(parts[1])

                            if "timeout" in parts:
                                last_rtt_str = "timeout"
                                avg_rtt_str = "timeout"
                                best_rtt_str = "timeout"
                                worst_rtt_str = "timeout"
                            else:
                                last_rtt_str = parts[2] if len(parts) > 2 else "0ms"
                                avg_rtt_str = "0"
                                best_rtt_str = "0"
                                worst_rtt_str = "0"

                            # Create timeout hop
                            hop = MikrotikTracerouteHop(
                                hop_number=current_hop_number,
                                ip_address=ip_address,
                                hostname=None,
                                loss_pct=loss_pct,
                                sent_count=sent_count,
                                last_rtt=parse_rtt(last_rtt_str),
                                avg_rtt=parse_rtt(avg_rtt_str),
                                best_rtt=parse_rtt(best_rtt_str),
                                worst_rtt=parse_rtt(worst_rtt_str),
                            )
                            hops.append(hop)
                            current_hop_number += 1
                            _log.debug(f"Line {i}: Created timeout hop {hop.hop_number}")
                            continue

                    if is_columnar_format:
                        # New format: "1  10.0.0.41         0%     1  0.5ms   0.5   0.5   0.5      0"
                        parts = line.split()
                        _log.debug(f"Line {i}: Columnar format, parts: {parts}")
                        if len(parts) < 3:
                            _log.debug(f"Line {i}: Too few parts ({len(parts)}), skipping")
                            continue

                        hop_number = int(parts[0])

                        # Check if there's an IP address or if it's empty (timeout hop)
                        if len(parts) >= 8 and not parts[1].endswith("%"):
                            # Normal hop with IP address
                            ip_address = parts[1] if parts[1] else None
                            loss_pct = int(parts[2].rstrip("%"))
                            sent_count = int(parts[3])
                            last_rtt_str = parts[4]
                            avg_rtt_str = parts[5]
                            best_rtt_str = parts[6]
                            worst_rtt_str = parts[7]
                        elif len(parts) >= 4 and parts[1].endswith("%"):
                            # Timeout hop without IP address
                            ip_address = None
                            loss_pct = int(parts[1].rstrip("%"))
                            sent_count = int(parts[2])
                            last_rtt_str = parts[3] if len(parts) > 3 else "timeout"
                            avg_rtt_str = "timeout"
                            best_rtt_str = "timeout"
                            worst_rtt_str = "timeout"
                        else:
                            _log.debug(f"Line {i}: Doesn't match columnar patterns, skipping")
                            continue
                    else:
                        # Old format: "196.60.8.198                       0%    1  17.1ms    17.1    17.1    17.1       0"
                        # We need to deduplicate by taking the LAST occurrence of each IP
                        parts = line.split()
                        _log.debug(f"Line {i}: Old format, parts: {parts}")
                        if len(parts) < 6:
                            _log.debug(f"Line {i}: Too few parts ({len(parts)}), skipping")
                            continue

                        ip_address = parts[0] if not parts[0].endswith("%") else None

                        # Check for truncated IPv6 addresses
                        if ip_address and (ip_address.endswith("...") or ip_address.endswith("..")):
                            _log.warning(
                                f"Line {i}: Truncated IP address detected: {ip_address} - setting to None"
                            )
                            ip_address = None

                        if ip_address:
                            loss_pct = int(parts[1].rstrip("%"))
                            sent_count = int(parts[2])
                            last_rtt_str = parts[3]
                            avg_rtt_str = parts[4]
                            best_rtt_str = parts[5]
                            worst_rtt_str = parts[6] if len(parts) > 6 else parts[5]
                        else:
                            # Timeout line or truncated address
                            if parts[0].endswith("%"):
                                # Normal timeout line
                                loss_pct = int(parts[0].rstrip("%"))
                                sent_count = int(parts[1])
                            else:
                                # Truncated address - extract stats from remaining parts
                                loss_pct = int(parts[1].rstrip("%"))
                                sent_count = int(parts[2])
                            last_rtt_str = "timeout"
                            avg_rtt_str = "timeout"
                            best_rtt_str = "timeout"
                            worst_rtt_str = "timeout"

                    # Convert timing values
                    def parse_rtt(rtt_str: str) -> t.Optional[float]:
                        if rtt_str in ("timeout", "-", "0ms"):
                            return None
                        # Remove 'ms' suffix and convert to float
                        rtt_clean = re.sub(r"ms$", "", rtt_str)
                        try:
                            return float(rtt_clean)
                        except ValueError:
                            return None

                    if is_columnar_format:
                        # Use hop number from the data and update our tracker
                        final_hop_number = hop_number
                        current_hop_number = max(current_hop_number, hop_number + 1)
                    else:
                        # Use sequential numbering for old format
                        final_hop_number = hop_counter
                        hop_counter += 1

                    hop_obj = MikrotikTracerouteHop(
                        hop_number=final_hop_number,
                        ip_address=ip_address,
                        hostname=None,  # MikroTik doesn't do reverse DNS by default
                        loss_pct=loss_pct,
                        sent_count=sent_count,
                        last_rtt=parse_rtt(last_rtt_str),
                        avg_rtt=parse_rtt(avg_rtt_str),
                        best_rtt=parse_rtt(best_rtt_str),
                        worst_rtt=parse_rtt(worst_rtt_str),
                    )

                    hops.append(hop_obj)
                    _log.debug(
                        f"Line {i}: Created hop {final_hop_number}: {ip_address} - {loss_pct}% - {sent_count} sent"
                    )

                except (ValueError, IndexError) as e:
                    _log.debug(f"Failed to parse line '{line}': {e}")
                    continue

        _log.debug(f"Before deduplication: {len(hops)} hops")

        # For old format, we need to deduplicate by IP and take only final stats
        if not is_columnar_format and hops:
            _log.debug(f"Old format detected - deduplicating {len(hops)} total entries")

            # Group by IP address and take the HIGHEST SENT count (final stats)
            ip_to_final_hop = {}
            ip_to_max_sent = {}
            hop_order = []

            for hop in hops:
                # Use IP address if available, otherwise use hop position for timeouts
                if hop.ip_address:
                    ip_key = hop.ip_address
                else:
                    # No IP address means timeout hop
                    ip_key = f"timeout_{hop.hop_number}"

                # Track first appearance order
                if ip_key not in hop_order:
                    hop_order.append(ip_key)
                    ip_to_max_sent[ip_key] = 0
                    _log.debug(f"New IP discovered: {ip_key}")

                # Keep hop with highest SENT count (most recent/final stats)
                if hop.sent_count and hop.sent_count >= ip_to_max_sent[ip_key]:
                    ip_to_max_sent[ip_key] = hop.sent_count
                    ip_to_final_hop[ip_key] = hop
                    _log.debug(f"Updated {ip_key}: SENT={hop.sent_count} (final stats)")

            _log.debug(f"IP order: {hop_order}")
            _log.debug(f"Final IP stats: {[(ip, ip_to_max_sent[ip]) for ip in hop_order]}")

            # Rebuild hops list with final stats and correct hop numbers
            final_hops = []
            for i, ip_key in enumerate(hop_order, 1):
                final_hop = ip_to_final_hop[ip_key]
                final_hop.hop_number = i  # Correct hop numbering
                final_hops.append(final_hop)
                _log.debug(
                    f"Final hop {i}: {ip_key} - Loss: {final_hop.loss_pct}% - Sent: {final_hop.sent_count}"
                )

            hops = final_hops
            _log.debug(f"Deduplication complete: {len(hops)} unique hops with final stats")

        _log.debug(f"After processing: {len(hops)} final hops")
        for hop in hops:
            _log.debug(
                f"Final hop {hop.hop_number}: {hop.ip_address} - {hop.loss_pct}% loss - {hop.sent_count} sent"
            )

        result = MikrotikTracerouteTable(target=target, source=source, hops=hops)
        _log.info(f"Parsed {len(hops)} hops from MikroTik traceroute final table")
        return result

    def traceroute_result(self):
        """Convert to TracerouteResult format."""
        from hyperglass.models.data.traceroute import TracerouteResult, TracerouteHop

        converted_hops = []
        for hop in self.hops:
            # Handle truncated IP addresses
            ip_address = hop.ip_address
            display_ip = None

            if hop.ip_address and hop.ip_address.endswith("..."):
                # For truncated IPs, store for display but set ip_address to None for validation
                display_ip = hop.ip_address
                ip_address = None

            converted_hops.append(
                TracerouteHop(
                    hop_number=hop.hop_number,
                    ip_address=ip_address,  # None for truncated IPs
                    display_ip=display_ip,  # Truncated IP for display
                    hostname=hop.hostname,
                    rtt1=hop.best_rtt,
                    rtt2=hop.avg_rtt,
                    rtt3=hop.worst_rtt,
                    # MikroTik-specific statistics
                    loss_pct=hop.loss_pct,
                    sent_count=hop.sent_count,
                    last_rtt=hop.last_rtt,
                    best_rtt=hop.best_rtt,
                    worst_rtt=hop.worst_rtt,
                    # BGP enrichment fields will be populated by enrichment plugin
                    # For truncated IPs, these will remain None/empty
                    asn=None,
                    org=None,
                    prefix=None,
                    country=None,
                    rir=None,
                    allocated=None,
                )
            )

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
