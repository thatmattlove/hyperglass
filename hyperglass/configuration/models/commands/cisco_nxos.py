"""Cisco NX-OS Command Model."""

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup

_ipv4_default = {
    "bgp_route": "show bgp ipv4 unicast {target}",
    "bgp_aspath": 'show bgp ipv4 unicast regexp "{target}"',
    "bgp_community": "show bgp ipv4 unicast community {target}",
    "ping": "ping {target} source {source}",
    "traceroute": "traceroute {target} source {source}",
}
_ipv6_default = {
    "bgp_route": "show bgp ipv6 unicast {target}",
    "bgp_aspath": 'show bgp ipv6 unicast regexp "{target}"',
    "bgp_community": "show bgp ipv6 unicast community {target}",
    "ping": "ping6 {target} source {source}",
    "traceroute": "traceroute6 {target} source {source}",
}
_ipv4_vpn = {
    "bgp_route": "show bgp ipv4 unicast {target} vrf {vrf}",
    "bgp_aspath": 'show bgp ipv4 unicast regexp "{target}" vrf {vrf}',
    "bgp_community": "show bgp ipv4 unicast community {target} vrf {vrf}",
    "ping": "ping {target} source {source} vrf {vrf}",
    "traceroute": "traceroute {target} source {source} vrf {vrf}",
}
_ipv6_vpn = {
    "bgp_route": "show bgp ipv6 unicast {target} vrf {vrf}",
    "bgp_aspath": 'show bgp ipv6 unicast regexp "{target}" vrf {vrf}',
    "bgp_community": "show bgp ipv6 unicast community {target} vrf {vrf}",
    "ping": "ping6 {target} source {source} vrf {vrf}",
    "traceroute": "traceroute6 {target} source {source} vrf {vrf}",
}


class CiscoNXOSCommands(CommandGroup):
    """Validation model for default cisco_nxos commands."""

    ipv4_default: CommandSet = CommandSet(**_ipv4_default)
    ipv6_default: CommandSet = CommandSet(**_ipv6_default)
    ipv4_vpn: CommandSet = CommandSet(**_ipv4_vpn)
    ipv6_vpn: CommandSet = CommandSet(**_ipv6_vpn)
