"""FRRouting Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: StrictStr = 'vtysh -c "show bgp ipv4 unicast community {target}"'
    bgp_aspath: StrictStr = 'vtysh -c "show bgp ipv4 unicast regexp {target}"'
    bgp_route: StrictStr = 'vtysh -c "show bgp ipv4 unicast {target}"'
    ping: StrictStr = "ping -4 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -4 -w 1 -q 1 -s {source} {target}"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: StrictStr = 'vtysh -c "show bgp ipv6 unicast community {target}"'
    bgp_aspath: StrictStr = 'vtysh -c "show bgp ipv6 unicast regexp {target}"'
    bgp_route: StrictStr = 'vtysh -c "show bgp ipv6 unicast {target}"'
    ping: StrictStr = "ping -6 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -6 -w 1 -q 1 -s {source} {target}"


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv4 unicast community {target}"'
    bgp_aspath: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv4 unicast regexp {target}"'
    bgp_route: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv4 unicast {target}"'
    ping: StrictStr = "ping -4 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -4 -w 1 -q 1 -s {source} {target}"


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv6 unicast community {target}"'
    bgp_aspath: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv6 unicast regexp {target}"'
    bgp_route: StrictStr = 'vtysh -c "show bgp vrf {vrf} ipv6 unicast {target}"'
    ping: StrictStr = "ping -6 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -6 -w 1 -q 1 -s {source} {target}"


class FRRCommands(CommandGroup):
    """Validation model for default FRRouting commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
