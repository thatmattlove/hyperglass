"""Cisco IOS XR Command Model."""

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup

_ipv4_default = {
    "bgp_route": "show bgp ipv4 unicast {target}",
    "bgp_aspath": "show bgp ipv4 unicast regexp {target}",
    "bgp_community": "show bgp ipv4 unicast community {target}",
    "ping": "ping ipv4 {target} count 5 source {source}",
    "traceroute": "traceroute ipv4 {target} timeout 1 probe 2 source {source}",
}
_ipv6_default = {
    "bgp_route": "show bgp ipv6 unicast {target}",
    "bgp_aspath": "show bgp ipv6 unicast regexp {target}",
    "bgp_community": "show bgp ipv6 unicast community {target}",
    "ping": "ping ipv6 {target} count 5 source {source}",
    "traceroute": "traceroute ipv6 {target} timeout 1 probe 2 source {source}",
}
_ipv4_vpn = {
    "bgp_route": "show bgp vpnv4 unicast vrf {vrf} {target}",
    "bgp_aspath": "show bgp vpnv4 unicast vrf {vrf} regexp {target}",
    "bgp_community": "show bgp vpnv4 unicast vrf {vrf} community {target}",
    "ping": "ping vrf {vrf} {target} count 5 source {source}",
    "traceroute": "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}",
}
_ipv6_vpn = {
    "bgp_route": "show bgp vpnv6 unicast vrf {vrf} {target}",
    "bgp_aspath": "show bgp vpnv6 unicast vrf {vrf} regexp {target}",
    "bgp_community": "show bgp vpnv6 unicast vrf {vrf} community {target}",
    "ping": "ping vrf {vrf} {target} count 5 source {source}",
    "traceroute": "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}",
}


class CiscoXRCommands(CommandGroup):
    """Validation model for default cisco_xr commands."""

    ipv4_default: CommandSet = CommandSet(**_ipv4_default)
    ipv6_default: CommandSet = CommandSet(**_ipv6_default)
    ipv4_vpn: CommandSet = CommandSet(**_ipv4_vpn)
    ipv6_vpn: CommandSet = CommandSet(**_ipv6_vpn)
