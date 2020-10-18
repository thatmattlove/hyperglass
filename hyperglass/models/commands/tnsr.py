"""Netgate TNSR Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for default VRF IPv4 commands."""

    bgp_community: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv4 unicast community {target}"'
    bgp_aspath: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv4 unicast regexp {target}"'
    bgp_route: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv4 unicast {target}"'
    ping: StrictStr = "ping {target} ipv4 source {source} count 5 timeout 1"
    traceroute: StrictStr = "traceroute {target} ipv4 source {source} timeout 1 waittime 1"


class _IPv6(CommandSet):
    """Validation model for default VRF IPv6 commands."""

    bgp_community: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv6 unicast community {target}"'
    bgp_aspath: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv6 unicast regexp {target}"'
    bgp_route: StrictStr = 'dataplane shell sudo vtysh -c "show bgp ipv6 unicast {target}"'
    ping: StrictStr = "ping {target} ipv6 source {source} count 5 timeout 1"
    traceroute: StrictStr = "traceroute {target} ipv6 source {source} timeout 1 waittime 1"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_community: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv4 unicast community {target}"'
    bgp_aspath: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv4 unicast regexp {target}"'
    bgp_route: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv4 unicast {target}"'
    ping: StrictStr = "dataplane shell ping -4 -c 5 -W 1 -I {vrf} -S {source} {target}"
    traceroute: StrictStr = "dataplane shell traceroute -4 -w 1 -q 1 -i {vrf} -s {source} {target}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_community: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv6 unicast community {target}"'
    bgp_aspath: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv6 unicast regexp {target}"'
    bgp_route: StrictStr = 'dataplane shell sudo vtysh -c "show bgp vrf {vrf} ipv6 unicast {target}"'
    ping: StrictStr = "dataplane shell ping -6 -c 5 -W 1 -I {vrf} -S {source} {target}"
    traceroute: StrictStr = "dataplane shell traceroute -6 -w 1 -q 1 -i {vrf} -s {source} {target}"


class TNSRCommands(CommandGroup):
    """Validation model for default tnsr commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
