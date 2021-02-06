"""BIRD Routing Daemon Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: str = 'birdc "show route all where {target} ~ bgp_community"'
    bgp_aspath: str = 'birdc "show route all where bgp_path ~ {target}"'
    bgp_route: str = 'birdc "show route all where {target} ~ net"'
    ping: str = "ping -4 -c 5 -I {source} {target}"
    traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: str = 'birdc "show route all where {target} ~ bgp_community"'
    bgp_aspath: str = 'birdc "show route all where bgp_path ~ {target}"'
    bgp_route: str = 'birdc "show route all where {target} ~ net"'
    ping: StrictStr = "ping -6 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -6 -w 1 -q 1 -s {source} {target}"


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: str = 'birdc "show route all table {vrf} where {target} ~ bgp_community"'
    bgp_aspath: str = 'birdc "show route all table {vrf} where bgp_path ~ {target}"'
    bgp_route: str = 'birdc "show route all table {vrf} where {target} ~ net"'
    ping: StrictStr = "ping -4 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -4 -w 1 -q 1 -s {source} {target}"


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: str = 'birdc "show route all table {vrf} where {target} ~ bgp_community"'
    bgp_aspath: str = 'birdc "show route all table {vrf} where bgp_path ~ {target}"'
    bgp_route: str = 'birdc "show route all table {vrf} where {target} ~ net"'
    ping: StrictStr = "ping -6 -c 5 -I {source} {target}"
    traceroute: StrictStr = "traceroute -6 -w 1 -q 1 -s {source} {target}"


class BIRDCommands(CommandGroup):
    """Validation model for default BIRD commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
