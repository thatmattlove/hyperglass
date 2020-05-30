"""Cisco NX-OS Command Model."""

# Third Party
from pydantic import StrictStr

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = "show bgp ipv4 unicast {target}"
    bgp_aspath: StrictStr = 'show bgp ipv4 unicast regexp "{target}"'
    bgp_community: StrictStr = "show bgp ipv4 unicast community {target}"
    ping: StrictStr = "ping {target} source {source}"
    traceroute: StrictStr = "traceroute {target} source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = "show bgp ipv6 unicast {target}"
    bgp_aspath: StrictStr = 'show bgp ipv6 unicast regexp "{target}"'
    bgp_community: StrictStr = "show bgp ipv6 unicast community {target}"
    ping: StrictStr = "ping6 {target} source {source}"
    traceroute: StrictStr = "traceroute6 {target} source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show bgp ipv4 unicast {target} vrf {vrf}"
    bgp_aspath: StrictStr = 'show bgp ipv4 unicast regexp "{target}" vrf {vrf}'
    bgp_community: StrictStr = "show bgp ipv4 unicast community {target} vrf {vrf}"
    ping: StrictStr = "ping {target} source {source} vrf {vrf}"
    traceroute: StrictStr = "traceroute {target} source {source} vrf {vrf}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show bgp ipv6 unicast {target} vrf {vrf}"
    bgp_aspath: StrictStr = 'show bgp ipv6 unicast regexp "{target}" vrf {vrf}'
    bgp_community: StrictStr = "show bgp ipv6 unicast community {target} vrf {vrf}"
    ping: StrictStr = "ping6 {target} source {source} vrf {vrf}"
    traceroute: StrictStr = "traceroute6 {target} source {source} vrf {vrf}"


class CiscoNXOSCommands(CommandGroup):
    """Validation model for default cisco_nxos commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
