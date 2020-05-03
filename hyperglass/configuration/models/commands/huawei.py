"""Huawei Command Model."""

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup

_ipv4_default = {
    "bgp_route": "display bgp routing-table {target}",
    "bgp_aspath": "display bgp routing-table regular-expression {target}",
    "bgp_community": "display bgp routing-table regular-expression {target}",
    "ping": "ping -c 5 -a {source} {target}",
    "traceroute": "tracert -q 2 -f 1 -a {source} {target}",
}
_ipv6_default = {
    "bgp_route": "display bgp ipv6 routing-table {target}",
    "bgp_aspath": "display bgp ipv6 routing-table regular-expression {target}",
    "bgp_community": "display bgp ipv6 routing-table community {target}",
    "ping": "ping ipv6 -c 5 -a {source} {target}",
    "traceroute": "tracert ipv6 -q 2 -f 1 -a {source} {target}",
}
_ipv4_vpn = {
    "bgp_route": "display bgp vpnv4 vpn-instance {vrf} routing-table {target}",
    "bgp_aspath": "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}",
    "bgp_community": "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}",
    "ping": "ping -vpn-instance {vrf} -c 5 -a {source} {target}",
    "traceroute": "tracert -q 2 -f 1 -vpn-instance {vrf} -a {source} {target}",
}
_ipv6_vpn = {
    "bgp_route": "display bgp vpnv6 vpn-instance {vrf} routing-table {target}",
    "bgp_aspath": "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}",
    "bgp_community": "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}",
    "ping": "ping vpnv6 vpn-instance {vrf} -c 5 -a {source} {target}",
    "traceroute": "tracert -q 2 -f 1 vpn-instance {vrf} -a {source} {target}",
}


class HuaweiCommands(CommandGroup):
    """Validation model for default huawei commands."""

    ipv4_default: CommandSet = CommandSet(**_ipv4_default)
    ipv6_default: CommandSet = CommandSet(**_ipv6_default)
    ipv4_vpn: CommandSet = CommandSet(**_ipv4_vpn)
    ipv6_vpn: CommandSet = CommandSet(**_ipv6_vpn)
