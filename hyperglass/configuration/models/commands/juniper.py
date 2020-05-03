"""Juniper Command Model."""

# Project
from hyperglass.configuration.models.commands.common import CommandSet, CommandGroup

_ipv4_default = {
    "bgp_route": 'show route protocol bgp table inet.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"',
    "bgp_aspath": 'show route protocol bgp table inet.0 aspath-regex "{target}"',
    "bgp_community": "show route protocol bgp table inet.0 community {target}",
    "ping": "ping inet {target} count 5 source {source}",
    "traceroute": "traceroute inet {target} wait 1 source {source}",
}
_ipv6_default = {
    "bgp_route": 'show route protocol bgp table inet6.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"',
    "bgp_aspath": 'show route protocol bgp table inet6.0 aspath-regex "{target}"',
    "bgp_community": "show route protocol bgp table inet6.0 community {target}",
    "ping": "ping inet6 {target} count 5 source {source}",
    "traceroute": "traceroute inet6 {target} wait 2 source {source}",
}
_ipv4_vpn = {
    "bgp_route": 'show route protocol bgp table {vrf}.inet.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"',
    "bgp_aspath": 'show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}"',
    "bgp_community": "show route protocol bgp table {vrf}.inet.0 community {target}",
    "ping": "ping inet routing-instance {vrf} {target} count 5 source {source}",
    "traceroute": "traceroute inet routing-instance {vrf} {target} wait 1 source {source}",
}
_ipv6_vpn = {
    "bgp_route": 'show route protocol bgp table {vrf}.inet6.0 {target} detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"',
    "bgp_aspath": 'show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}"',
    "bgp_community": "show route protocol bgp table {vrf}.inet6.0 community {target}",
    "ping": "ping inet6 routing-instance {vrf} {target} count 5 source {source}",
    "traceroute": "traceroute inet6 routing-instance {vrf} {target} wait 2 source {source}",
}

_structured = CommandGroup(
    ipv4_default=CommandSet(
        bgp_route="show route protocol bgp table inet.0 {target} detail | display json",
        bgp_aspath='show route protocol bgp table inet.0 aspath-regex "{target}" | display json',
        bgp_community="show route protocol bgp table inet.0 community {target} | display json",
        ping="ping inet {target} count 5 source {source}",
        traceroute="traceroute inet {target} wait 1 source {source}",
    ),
    ipv6_default=CommandSet(
        bgp_route="show route protocol bgp table inet6.0 {target} detail | display json",
        bgp_aspath='show route protocol bgp table inet6.0 aspath-regex "{target}" | display json',
        bgp_community="show route protocol bgp table inet6.0 community {target} | display json",
        ping="ping inet6 {target} count 5 source {source}",
        traceroute="traceroute inet6 {target} wait 2 source {source}",
    ),
    ipv4_vpn=CommandSet(
        bgp_route="show route protocol bgp table {vrf}.inet.0 {target} detail | display json",
        bgp_aspath='show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}" | display json',
        bgp_community="show route protocol bgp table {vrf}.inet.0 community {target} | display json",
        ping="ping inet routing-instance {vrf} {target} count 5 source {source}",
        traceroute="traceroute inet routing-instance {vrf} {target} wait 1 source {source}",
    ),
    ipv6_vpn=CommandSet(
        bgp_route="show route protocol bgp table {vrf}.inet6.0 {target} detail | display json",
        bgp_aspath='show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}" | display json',
        bgp_community="show route protocol bgp table {vrf}.inet6.0 community {target} | display json",
        ping="ping inet6 routing-instance {vrf} {target} count 5 source {source}",
        traceroute="traceroute inet6 routing-instance {vrf} {target} wait 1 source {source}",
    ),
)


class JuniperCommands(CommandGroup):
    """Validation model for default juniper commands."""

    ipv4_default: CommandSet = CommandSet(**_ipv4_default)
    ipv6_default: CommandSet = CommandSet(**_ipv6_default)
    ipv4_vpn: CommandSet = CommandSet(**_ipv4_vpn)
    ipv6_vpn: CommandSet = CommandSet(**_ipv6_vpn)
    structured: CommandGroup = _structured
