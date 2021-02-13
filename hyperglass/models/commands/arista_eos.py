"""Arista EOS Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = "show ip bgp {target}"
    bgp_aspath: StrictStr = "show ip bgp regexp {target}"
    bgp_community: StrictStr = "show ip bgp community {target}"
    ping: StrictStr = "ping ip {target} source {source}"
    traceroute: StrictStr = "traceroute ip {target} source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = "show ipv6 bgp {target}"
    bgp_aspath: StrictStr = "show ipv6 bgp regexp {target}"
    bgp_community: StrictStr = "show ipv6 bgp community {target}"
    ping: StrictStr = "ping ipv6 {target} source {source}"
    traceroute: StrictStr = "traceroute ipv6 {target} source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show ip bgp {target} vrf {vrf}"
    bgp_aspath: StrictStr = "show ip bgp regexp {target} vrf {vrf}"
    bgp_community: StrictStr = "show ip bgp community {target} vrf {vrf}"
    ping: StrictStr = "ping vrf {vrf} ip {target} source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} ip {target} source {source}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show ipv6 bgp {target} vrf {vrf}"
    bgp_aspath: StrictStr = "show ipv6 bgp regexp {target} vrf {vrf}"
    bgp_community: StrictStr = "show ipv6 bgp community {target} vrf {vrf}"
    ping: StrictStr = "ping vrf {vrf} ipv6 {target} source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} ipv6 {target} source {source}"


_structured = CommandGroup(
    ipv4_default=CommandSet(
        bgp_route="show ip bgp {target} | json",
        bgp_aspath="show ip bgp regexp {target} | json",
        bgp_community="show ip bgp community {target} | json",
        ping="ping ip {target} source {source}",
        traceroute="traceroute ip {target} source {source}",
    ),
    ipv6_default=CommandSet(
        bgp_route="show ipv6 bgp {target} | json",
        bgp_aspath="show ipv6 bgp regexp {target} | json",
        bgp_community="show ipv6 bgp community {target} | json",
        ping="ping ipv6 {target} source {source}",
        traceroute="traceroute ipv6 {target} source {source}",
    ),
    ipv4_vpn=CommandSet(
        bgp_route="show ip bgp {target} vrf {vrf} | json",
        bgp_aspath="show ip bgp regexp {target} vrf {vrf} | json",
        bgp_community="show ip bgp community {target} vrf {vrf} | json",
        ping="ping vrf {vrf} ip {target} source {source}",
        traceroute="traceroute vrf {vrf} ip {target} source {source}",
    ),
    ipv6_vpn=CommandSet(
        bgp_route="show ipv6 bgp {target} vrf {vrf} | json",
        bgp_aspath="show ipv6 bgp regexp {target} vrf {vrf} | json",
        bgp_community="show ipv6 bgp community {target} vrf {vrf} | json",
        ping="ping vrf {vrf} ipv6 {target} source {source}",
        traceroute="traceroute vrf {vrf} ipv6 {target} source {source}",
    ),
)


class AristaEOSCommands(CommandGroup):
    """Validation model for default arista_eos commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()

    def __init__(self, **kwargs):
        """Initialize command group, ensure structured fields are not overridden."""
        super().__init__(**kwargs)
        self.structured = _structured
