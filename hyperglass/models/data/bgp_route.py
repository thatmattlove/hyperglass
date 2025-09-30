"""Device-Agnostic Parsed Response Data Model."""

# Standard Library
import re
import typing as t
from ipaddress import ip_network

# Third Party
from pydantic import ValidationInfo, field_validator

# Project
from hyperglass.state import use_state
from hyperglass.external.rpki import rpki_state
from hyperglass.external.ip_enrichment import TargetDetail

# Local
from ..main import HyperglassModel

WinningWeight = t.Literal["low", "high"]


class BGPRoute(HyperglassModel):
    """Post-parsed BGP route."""

    prefix: str
    active: bool
    age: int
    weight: int
    med: int
    local_preference: int
    as_path: t.List[int]
    communities: t.List[str]
    next_hop: str
    source_as: int
    source_rid: str
    peer_rid: str
    rpki_state: int

    # IP enrichment data (optional)
    next_hop_asn: t.Optional[str] = None
    next_hop_org: t.Optional[str] = None
    next_hop_country: t.Optional[str] = None

    @field_validator("communities")
    def validate_communities(cls, value):
        """Filter returned communities against configured policy.

        Actions:
            permit: only permit matches
            deny: only deny matches
            name: append friendly names to matching communities
        """

        (structured := use_state("params").structured)

        def _permit(comm):
            """Only allow matching patterns."""
            valid = False
            for pattern in structured.communities.items:
                if re.match(pattern, comm):
                    valid = True
                    break
            return valid

        def _deny(comm):
            """Allow any except matching patterns."""
            valid = True
            for pattern in structured.communities.items:
                if re.match(pattern, comm):
                    valid = False
                    break
            return valid

        def _name(comm):
            """Append friendly names to matching communities."""
            # Check if this community has a friendly name mapping
            if comm in structured.communities.names:
                return f"{comm},{structured.communities.names[comm]}"
            return comm

        if structured.communities.mode == "name":
            # For name mode, transform communities to include friendly names
            return [_name(c) for c in value]
        else:
            # For permit/deny modes, use existing filtering logic
            func_map = {"permit": _permit, "deny": _deny}
            func = func_map[structured.communities.mode]
            return [c for c in value if func(c)]

    @field_validator("rpki_state")
    def validate_rpki_state(cls, value, info: ValidationInfo):
        """If external RPKI validation is enabled, get validation state."""
        (structured := use_state("params").structured)

        if structured.rpki.mode == "router":
            # If router validation is enabled, return the value as-is.
            return value

        if structured.rpki.mode == "external":
            as_path = info.data.get("as_path", [])
            if len(as_path) == 0:
                # If the AS_PATH length is 0, i.e. for an internal route,
                # return RPKI Unknown state.
                return 3
            # Get last ASN in path
            asn = as_path[-1]

            try:
                net = ip_network(info.data["prefix"])
            except ValueError:
                return 3

            if net.is_global:
                backend = getattr(structured.rpki, "backend", "cloudflare")
                rpki_server_url = getattr(structured.rpki, "rpki_server_url", "")
                return rpki_state(
                    prefix=info.data["prefix"],
                    asn=asn,
                    backend=backend,
                    rpki_server_url=rpki_server_url,
                )

        return value

    @property
    def as_path_summary(self) -> str:
        """Summary of AS path."""
        if not self.as_path:
            return "Unknown"
        return " -> ".join([f"AS{asn}" for asn in self.as_path])

    async def get_as_path_detailed(self) -> str:
        """Detailed AS path with organization names using IP enrichment."""
        if not self.as_path:
            return "Unknown"

        try:
            from hyperglass.external.ip_enrichment import lookup_asn_name

            detailed_path = []
            for asn in self.as_path:
                try:
                    org_name = await lookup_asn_name(asn)
                    if org_name and org_name != f"AS{asn}":
                        detailed_path.append(f"AS{asn} ({org_name})")
                    else:
                        detailed_path.append(f"AS{asn}")
                except Exception:
                    detailed_path.append(f"AS{asn}")

            return " -> ".join(detailed_path)
        except Exception:
            return self.as_path_summary


class BGPRouteTable(HyperglassModel):
    """Post-parsed BGP route table."""

    vrf: str
    count: int = 0
    routes: t.List[BGPRoute]
    winning_weight: WinningWeight
    asn_organizations: t.Dict[str, t.Dict[str, str]] = {}  # ASN -> {name, country}

    def __init__(self, **kwargs):
        """Sort routes by prefix after validation."""
        super().__init__(**kwargs)
        self.routes = sorted(self.routes, key=lambda r: r.prefix)

    def __add__(self: "BGPRouteTable", other: "BGPRouteTable") -> "BGPRouteTable":
        """Merge another BGP table instance with this instance."""
        if isinstance(other, BGPRouteTable):
            self.routes = sorted([*self.routes, *other.routes], key=lambda r: r.prefix)
            self.count = len(self.routes)
        return self

    async def enrich_with_ip_enrichment(self):
        """Enrich BGP routes with next-hop information from IP enrichment."""
        from hyperglass.external.ip_enrichment import network_info

        # Extract unique next-hop IPs that need enrichment
        next_hops_to_lookup = set()
        for route in self.routes:
            if route.next_hop and not route.next_hop_asn:  # Only lookup if not already enriched
                next_hops_to_lookup.add(route.next_hop)

        if not next_hops_to_lookup:
            return

        # Bulk lookup next-hop information
        network_data = await network_info(*list(next_hops_to_lookup))

        # Enrich routes with the retrieved data
        for route in self.routes:
            if route.next_hop in network_data:
                data: TargetDetail = network_data[route.next_hop]
                # Handle ASN formatting
                asn_raw = data.get("asn")
                if asn_raw and asn_raw != "None":
                    route.next_hop_asn = f"AS{asn_raw}"
                else:
                    route.next_hop_asn = None

                route.next_hop_org = data.get("org") if data.get("org") != "None" else None
                route.next_hop_country = (
                    data.get("country") if data.get("country") != "None" else None
                )

    async def enrich_as_path_organizations(self):
        """Enrich AS path ASNs with organization names using bulk lookup."""
        from hyperglass.external.ip_enrichment import lookup_asns_bulk
        from hyperglass.log import log

        _log = log.bind(source="bgp_asn_enrichment")

        # Collect all unique ASNs from AS paths
        all_asns = set()
        for route in self.routes:
            all_asns.update(route.as_path)

        if not all_asns:
            _log.debug("No AS paths found to enrich")
            return

        # Convert to strings and bulk lookup
        asn_strings = [str(asn) for asn in all_asns]
        _log.warning(
            f"🔍 BGP AS PATH ENRICHMENT STARTED - Looking up {len(asn_strings)} ASNs: {asn_strings}"
        )

        try:
            asn_data = await lookup_asns_bulk(asn_strings)
            _log.debug(f"Got ASN organization data: {asn_data}")

            # Store the ASN organization mapping for use by frontend
            self.asn_organizations = asn_data
            _log.warning(
                f"🔍 BGP AS PATH ENRICHMENT SUCCESS - Enriched with {len(asn_data)} ASN organizations: {asn_data}"
            )

        except Exception as e:
            _log.error(f"Failed to lookup ASN organizations: {e}")
            self.asn_organizations = {}
