"""Arista Command Model."""

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup

_ipv4_default = {
    "bgp_route": "show ip bgp {target}",
    "bgp_aspath": "show ip bgp regexp {target}",
    "bgp_community": "show ip bgp community {target}",
    "ping": "ping ip {target} source {source}",
    "traceroute": "traceroute ip {target} source {source}",
}
_ipv6_default = {
    "bgp_route": "show ipv6 bgp {target}",
    "bgp_aspath": "show ipv6 bgp regexp {target}",
    "bgp_community": "show ipv6 bgp community {target}",
    "ping": "ping ipv6 {target} source {source}",
    "traceroute": "traceroute ipv6 {target} source {source}",
}
_ipv4_vpn = {
    "bgp_route": "show ip bgp {target} vrf {vrf}",
    "bgp_aspath": "show ip bgp regexp {target} vrf {vrf}",
    "bgp_community": "show ip bgp community {target} vrf {vrf}",
    "ping": "ping vrf {vrf} ip {target} source {source}",
    "traceroute": "traceroute vrf {vrf} ip {target} source {source}",
}
_ipv6_vpn = {
    "bgp_route": "show ipv6 bgp {target} vrf {vrf}",
    "bgp_aspath": "show ipv6 bgp regexp {target} vrf {vrf}",
    "bgp_community": "show ipv6 bgp community {target} vrf {vrf}",
    "ping": "ping vrf {vrf} ipv6 {target} source {source}",
    "traceroute": "traceroute vrf {vrf} ipv6 {target} source {source}",
}


class AristaCommands(CommandGroup):
    """Validation model for default arista commands."""

    ipv4_default: CommandSet = CommandSet(**_ipv4_default)
    ipv6_default: CommandSet = CommandSet(**_ipv6_default)
    ipv4_vpn: CommandSet = CommandSet(**_ipv4_vpn)
    ipv6_vpn: CommandSet = CommandSet(**_ipv6_vpn)
