"""Base Mikrotik Commands Model."""

# Third Party
from pydantic import StrictStr

from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Default commands for ipv4 commands."""

    bgp_community: StrictStr = "ip route print where bgp-communities={target}"
    bgp_aspath: StrictStr = "ip route print where bgp-as-path={target}"
    bgp_route: StrictStr = "ip route print where dst-address={target}"
    ping: StrictStr = "ping src-address={source} count=5 {target}"
    traceroute: StrictStr = "tool traceroute src-address={source} timeout=1 duration=5 count=1 {target}"


class _IPv6(CommandSet):
    """Default commands for ipv6 commands."""

    bgp_community: StrictStr = "ipv6 route print where bgp-communities={target}"
    bgp_aspath: StrictStr = "ipv6 route print where bgp-as-path={target}"
    bgp_route: StrictStr = "ipv6 route print where dst-address={target}"
    ping: StrictStr = "ping src-address={source} count=5 {target}"
    traceroute: StrictStr = "tool traceroute src-address={source} timeout=1 duration=5 count=1 {target}"


class _VPNIPv4(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "ip route print where bgp-communities={target} routing-mark={vrf}"
    bgp_aspath: StrictStr = "ip route print where bgp-as-path={target} routing-mark={vrf}"
    bgp_route: StrictStr = "ip route print where dst-address={target} routing-mark={vrf}"
    ping: StrictStr = "ping src-address={source} count=5 routing-table={vrf} {target}"
    traceroute: StrictStr = "tool traceroute src-address={source} timeout=1 duration=5 count=1 routing-table={vrf} {target}"


class _VPNIPv6(CommandSet):
    """Default commands for dual afi commands."""

    bgp_community: StrictStr = "ipv6 route print where bgp-communities={target} routing-mark={vrf}"
    bgp_aspath: StrictStr = "ipv6 route print where bgp-as-path={target} routing-mark={vrf}"
    bgp_route: StrictStr = "ipv6 route print where dst-address={target} routing-mark={vrf}"
    ping: StrictStr = "ping src-address={source} count=5 routing-table={vrf} {target}"
    traceroute: StrictStr = "tool traceroute src-address={source} timeout=1 duration=5 count=1 routing-table={vrf} {target}"


class MikrotikCommands(CommandGroup):
    """Validation model for default mikrotik commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()
