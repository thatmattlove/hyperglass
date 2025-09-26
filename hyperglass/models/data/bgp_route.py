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


class BGPRouteTable(HyperglassModel):
    """Post-parsed BGP route table."""

    vrf: str
    count: int = 0
    routes: t.List[BGPRoute]
    winning_weight: WinningWeight

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
