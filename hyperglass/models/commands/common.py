"""Models common to entire commands module."""

# Third Party
from pydantic import StrictStr

from ..main import HyperglassModel, HyperglassModelExtra


class CommandSet(HyperglassModel):
    """Command set, defined per-AFI."""

    bgp_route: StrictStr
    bgp_aspath: StrictStr
    bgp_community: StrictStr
    ping: StrictStr
    traceroute: StrictStr


class CommandGroup(HyperglassModelExtra):
    """Validation model for all commands."""

    ipv4_default: CommandSet
    ipv6_default: CommandSet
    ipv4_vpn: CommandSet
    ipv6_vpn: CommandSet
