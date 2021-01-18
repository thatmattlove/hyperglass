"""Nokia SR-OS Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: StrictStr = "/show router bgp routes community {target}"
    bgp_aspath: StrictStr = "/show router bgp routes aspath-regex {target}"
    bgp_route: StrictStr = "/show router bgp routes {target} ipv4 hunt"
    ping: StrictStr = "/ping {target} source-address {source}"
    traceroute: StrictStr = "/traceroute {target} source-address {source} wait 2 seconds"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: StrictStr = "/show router bgp routes community {target}"
    bgp_aspath: StrictStr = "/show router bgp routes aspath-regex {target}"
    bgp_route: StrictStr = "/show router bgp routes {target} ipv6 hunt"
    ping: StrictStr = "/ping {target} source-address {source}"
    traceroute: StrictStr = "/traceroute {target} source-address {source} wait 2 seconds"


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "/show router bgp routes community {target}"
    bgp_aspath: StrictStr = "/show router bgp routes aspath-regex {target}"
    bgp_route: StrictStr = "/show router bgp routes {target} vpn-ipv4 hunt"
    ping: StrictStr = "/ping {target} source-address {source}"
    traceroute: StrictStr = "/traceroute {target} source-address {source} wait 2 seconds"


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "/show router bgp routes community {target}"
    bgp_aspath: StrictStr = "/show router bgp routes aspath-regex {target}"
    bgp_route: StrictStr = "/show router bgp routes {target} vpn-ipv6 hunt"
    ping: StrictStr = "/ping {target} source-address {source}"
    traceroute: StrictStr = "/traceroute {target} source-address {source} wait 2 seconds"


class NokiaSROSCommands(CommandGroup):
    """Validation model for default nokia_sros commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
