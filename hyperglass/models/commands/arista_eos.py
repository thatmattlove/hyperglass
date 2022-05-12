"""Arista EOS Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = "show ip bgp {target} | json"
    bgp_aspath: StrictStr = "show ip bgp regexp {target} | json"
    bgp_community: StrictStr = "show ip bgp community {target} | json"
    ping: StrictStr = "ping ip {target} source {source}"
    traceroute: StrictStr = "traceroute ip {target} source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = "show ipv6 bgp {target} | json"
    bgp_aspath: StrictStr = "show ipv6 bgp regexp {target} | json"
    bgp_community: StrictStr = "show ipv6 bgp community {target} | json"
    ping: StrictStr = "ping ipv6 {target} source {source}"
    traceroute: StrictStr = "traceroute ipv6 {target} source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show ip bgp {target} vrf {vrf} | json"
    bgp_aspath: StrictStr = "show ip bgp regexp {target} vrf {vrf} | json"
    bgp_community: StrictStr = "show ip bgp community {target} vrf {vrf} | json"
    ping: StrictStr = "ping vrf {vrf} ip {target} source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} ip {target} source {source}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = "show ipv6 bgp {target} vrf {vrf} | json"
    bgp_aspath: StrictStr = "show ipv6 bgp regexp {target} vrf {vrf} | json"
    bgp_community: StrictStr = "show ipv6 bgp community {target} vrf {vrf} | json"
    ping: StrictStr = "ping vrf {vrf} ipv6 {target} source {source}"
    traceroute: StrictStr = "traceroute vrf {vrf} ipv6 {target} source {source}"


class AristaEOSCommands(CommandGroup):
    """Validation model for default arista_eos commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.structured = CommandGroup(
            ipv4_default=self.ipv4_default,
            ipv6_default=self.ipv6_default,
            ipv4_vpn=self.ipv4_vpn,
            ipv6_vpn=self.ipv6_vpn,
        )
