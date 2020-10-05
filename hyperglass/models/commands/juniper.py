"""Juniper Command Model."""

# Third Party
from pydantic import StrictStr

from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = 'show route protocol bgp table inet.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table inet.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table inet.0 community {target}"
    ping: StrictStr = "ping inet {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet {target} wait 1 source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table inet6.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table inet6.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table inet6.0 community {target}"
    ping: StrictStr = "ping inet6 {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet6 {target} wait 2 source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table {vrf}.inet.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet.0 community {target}"
    ping: StrictStr = "ping inet routing-instance {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet routing-instance {vrf} {target} wait 1 source {source}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table {vrf}.inet6.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet6.0 community {target}"
    ping: StrictStr = "ping inet6 routing-instance {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet6 routing-instance {vrf} {target} wait 2 source {source}"


_structured = CommandGroup(
    ipv4_default=CommandSet(
        bgp_route="show route protocol bgp table inet.0 {target} detail | display xml",
        bgp_aspath='show route protocol bgp table inet.0 aspath-regex "{target}" detail | display xml',
        bgp_community="show route protocol bgp table inet.0 community {target} detail | display xml",
        ping="ping inet {target} count 5 source {source}",
        traceroute="traceroute inet {target} wait 1 source {source}",
    ),
    ipv6_default=CommandSet(
        bgp_route="show route protocol bgp table inet6.0 {target} detail | display xml",
        bgp_aspath='show route protocol bgp table inet6.0 aspath-regex "{target}" detail | display xml',
        bgp_community="show route protocol bgp table inet6.0 community {target} detail | display xml",
        ping="ping inet6 {target} count 5 source {source}",
        traceroute="traceroute inet6 {target} wait 2 source {source}",
    ),
    ipv4_vpn=CommandSet(
        bgp_route="show route protocol bgp table {vrf}.inet.0 {target} detail | display xml",
        bgp_aspath='show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}" detail | display xml',
        bgp_community="show route protocol bgp table {vrf}.inet.0 community {target} detail | display xml",
        ping="ping inet routing-instance {vrf} {target} count 5 source {source}",
        traceroute="traceroute inet routing-instance {vrf} {target} wait 1 source {source}",
    ),
    ipv6_vpn=CommandSet(
        bgp_route="show route protocol bgp table {vrf}.inet6.0 {target} detail | display xml",
        bgp_aspath='show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}" detail | display xml',
        bgp_community="show route protocol bgp table {vrf}.inet6.0 community {target} detail | display xml",
        ping="ping inet6 routing-instance {vrf} {target} count 5 source {source}",
        traceroute="traceroute inet6 routing-instance {vrf} {target} wait 1 source {source}",
    ),
)


class JuniperCommands(CommandGroup):
    """Validation model for default juniper commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()

    def __init__(self, **kwargs):
        """Initialize command group, ensure structured fields are not overridden."""
        super().__init__(**kwargs)
        self.structured = _structured
