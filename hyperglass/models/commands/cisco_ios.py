"""Cisco IOS Command Model."""

# Third Party
from pydantic import StrictStr

from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: StrictStr = "show bgp ipv4 unicast community {target}"
    bgp_aspath: StrictStr = 'show bgp ipv4 unicast quote-regexp "{target}"'
    bgp_route: StrictStr = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
    ping: StrictStr = "ping {target} repeat 5 source {source}"
    traceroute: StrictStr = "traceroute {target} timeout 1 probe 2 source {source}"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: StrictStr = "show bgp ipv6 unicast community {target}"
    bgp_aspath: StrictStr = 'show bgp ipv6 unicast quote-regexp "{target}"'
    bgp_route: StrictStr = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
    ping: StrictStr = "ping ipv6 {target} repeat 5 source {source}"
    traceroute: StrictStr = (
        "traceroute ipv6 {target} timeout 1 probe 2 source {source}"
    )


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "show bgp vpnv4 unicast vrf {vrf} community {target}"
    bgp_aspath: StrictStr = 'show bgp vpnv4 unicast vrf {vrf} quote-regexp "{target}"'
    bgp_route: StrictStr = "show bgp vpnv4 unicast vrf {vrf} {target}"
    ping: StrictStr = "ping vrf {vrf} {target} repeat 5 source {source}"
    traceroute: StrictStr = (
        "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
    )


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "show bgp vpnv6 unicast vrf {vrf} community {target}"
    bgp_aspath: StrictStr = 'show bgp vpnv6 unicast vrf {vrf} quote-regexp "{target}"'
    bgp_route: StrictStr = "show bgp vpnv6 unicast vrf {vrf} {target}"
    ping: StrictStr = "ping vrf {vrf} {target} repeat 5 source {source}"
    traceroute: StrictStr = (
        "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
    )


class CiscoIOSCommands(CommandGroup):
    """Validation model for default cisco_ios commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
