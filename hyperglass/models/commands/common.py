"""Models common to entire commands module."""

# Third Party
from pydantic import StrictStr

# Local
from ..main import HyperglassModel


class CommandSet(HyperglassModel):
    """Command set, defined per-AFI."""

    bgp_route: StrictStr
    bgp_aspath: StrictStr
    bgp_community: StrictStr
    ping: StrictStr
    traceroute: StrictStr


class CommandGroup(HyperglassModel, extra="allow"):
    """Validation model for all commands."""

    ipv4_default: CommandSet
    ipv6_default: CommandSet
    ipv4_vpn: CommandSet
    ipv6_vpn: CommandSet
