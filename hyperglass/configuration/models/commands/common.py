"""Models common to entire commands module."""

from typing import Optional

# Third Party
from pydantic import StrictStr

# Project
from hyperglass.models import HyperglassModel


class CommandSet(HyperglassModel):
    """Command set, defined per-AFI."""

    bgp_route: StrictStr
    bgp_aspath: StrictStr
    bgp_community: StrictStr
    ping: StrictStr
    traceroute: StrictStr


class CommandGroup(HyperglassModel):
    """Validation model for all commands."""

    ipv4_default: CommandSet
    ipv6_default: CommandSet
    ipv4_vpn: CommandSet
    ipv6_vpn: CommandSet
    structured: Optional["CommandGroup"]


CommandGroup.update_forward_refs()
