"""Cisco IOS XR Command Model."""

# Third Party
from pydantic import StrictStr

from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = "show bgp ipv4 unicast {target}"
    bgp_aspath: StrictStr = "show bgp ipv4 unicast regexp {target}"
    bgp_community: StrictStr = "show bgp ipv4 unicast community {target}"
    ping: StrictStr = "ping ipv4 {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute ipv4 {target} timeout 1 probe 2 source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = "show bgp ipv6 unicast {target}"
    bgp_aspath: StrictStr = "show bgp ipv6 unicast regexp {target}"
    bgp_community: StrictStr = "show bgp ipv6 unicast community {target}"
    ping: StrictStr = "ping ipv6 {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute ipv6 {target} timeout 1 probe 2 source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show bgp vpnv4 unicast vrf {vrf} {target}"
    bgp_aspath: StrictStr = "show bgp vpnv4 unicast vrf {vrf} regexp {target}"
    bgp_community: StrictStr = "show bgp vpnv4 unicast vrf {vrf} community {target}"
    ping: StrictStr = "ping vrf {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show bgp vpnv6 unicast vrf {vrf} {target}"
    bgp_aspath: StrictStr = "show bgp vpnv6 unicast vrf {vrf} regexp {target}"
    bgp_community: StrictStr = "show bgp vpnv6 unicast vrf {vrf} community {target}"
    ping: StrictStr = "ping vrf {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"


class CiscoXRCommands(CommandGroup):
    """Validation model for default cisco_xr commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
