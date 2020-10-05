"""Huawei Command Model."""

# Third Party
from pydantic import StrictStr

from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: StrictStr = "display bgp routing-table regular-expression {target}"
    bgp_aspath: StrictStr = "display bgp routing-table regular-expression {target}"
    bgp_route: StrictStr = "display bgp routing-table {target}"
    ping: StrictStr = "ping -c 5 -a {source} {target}"
    traceroute: StrictStr = "tracert -q 2 -f 1 -a {source} {target}"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: StrictStr = "display bgp ipv6 routing-table community {target}"
    bgp_aspath: StrictStr = "display bgp ipv6 routing-table regular-expression {target}"
    bgp_route: StrictStr = "display bgp ipv6 routing-table {target}"
    ping: StrictStr = "ping ipv6 -c 5 -a {source} {target}"
    traceroute: StrictStr = "tracert ipv6 -q 2 -f 1 -a {source} {target}"


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
    bgp_aspath: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
    bgp_route: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table {target}"
    ping: StrictStr = "ping -vpn-instance {vrf} -c 5 -a {source} {target}"
    traceroute: StrictStr = "tracert -q 2 -f 1 -vpn-instance {vrf} -a {source} {target}"


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
    bgp_aspath: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
    bgp_route: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table {target}"
    ping: StrictStr = "ping vpnv6 vpn-instance {vrf} -c 5 -a {source} {target}"
    traceroute: StrictStr = "tracert -q 2 -f 1 vpn-instance {vrf} -a {source} {target}"


class HuaweiCommands(CommandGroup):
    """Validation model for default huawei commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
