"""Validate command configuration variables."""

# Third Party
from pydantic import StrictStr

# Project
from hyperglass.configuration.models._utils import HyperglassModel


class Command(HyperglassModel):
    """Validation model for non-default commands."""

    class IPv4(HyperglassModel):
        """Validation model for non-default dual afi commands."""

        bgp_route: StrictStr
        bgp_aspath: StrictStr
        bgp_community: StrictStr
        ping: StrictStr
        traceroute: StrictStr

    class IPv6(HyperglassModel):
        """Validation model for non-default ipv4 commands."""

        bgp_route: StrictStr
        bgp_aspath: StrictStr
        bgp_community: StrictStr
        ping: StrictStr
        traceroute: StrictStr

    class VPNIPv4(HyperglassModel):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr
        bgp_aspath: StrictStr
        bgp_community: StrictStr
        ping: StrictStr
        traceroute: StrictStr

    class VPNIPv6(HyperglassModel):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr
        bgp_aspath: StrictStr
        bgp_community: StrictStr
        ping: StrictStr
        traceroute: StrictStr

    ipv4_default: IPv4
    ipv6_default: IPv6
    ipv4_vpn: VPNIPv4
    ipv6_vpn: VPNIPv6


class CiscoIOS(Command):
    """Validation model for default cisco_ios commands."""

    class VPNIPv4(Command.VPNIPv4):
        """Default commands for dual afi commands."""

        bgp_community: StrictStr = "show bgp vpnv4 unicast vrf {vrf} community {target}"
        bgp_aspath: StrictStr = 'show bgp vpnv4 unicast vrf {vrf} quote-regexp "{target}"'
        bgp_route: StrictStr = "show bgp vpnv4 unicast vrf {vrf} {target}"
        ping: StrictStr = "ping vrf {vrf} {target} repeat 5 source {source}"
        traceroute: StrictStr = (
            "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
        )

    class VPNIPv6(Command.VPNIPv6):
        """Default commands for dual afi commands."""

        bgp_community: StrictStr = "show bgp vpnv6 unicast vrf {vrf} community {target}"
        bgp_aspath: StrictStr = 'show bgp vpnv6 unicast vrf {vrf} quote-regexp "{target}"'
        bgp_route: StrictStr = "show bgp vpnv6 unicast vrf {vrf} {target}"
        ping: StrictStr = "ping vrf {vrf} {target} repeat 5 source {source}"
        traceroute: StrictStr = (
            "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
        )

    class IPv4(Command.IPv4):
        """Default commands for ipv4 commands."""

        bgp_community: StrictStr = "show bgp ipv4 unicast community {target}"
        bgp_aspath: StrictStr = 'show bgp ipv4 unicast quote-regexp "{target}"'
        bgp_route: StrictStr = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
        ping: StrictStr = "ping {target} repeat 5 source {source}"
        traceroute: StrictStr = "traceroute {target} timeout 1 probe 2 source {source}"

    class IPv6(Command.IPv6):
        """Default commands for ipv6 commands."""

        bgp_community: StrictStr = "show bgp ipv6 unicast community {target}"
        bgp_aspath: StrictStr = 'show bgp ipv6 unicast quote-regexp "{target}"'
        bgp_route: StrictStr = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
        ping: StrictStr = ("ping ipv6 {target} repeat 5 source {source}")
        traceroute: StrictStr = (
            "traceroute ipv6 {target} timeout 1 probe 2 source {source}"
        )

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class CiscoXR(Command):
    """Validation model for default cisco_xr commands."""

    class IPv4(Command.IPv4):
        """Validation model for non-default dual afi commands."""

        bgp_route: StrictStr = r"show bgp ipv4 unicast {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
        bgp_aspath: StrictStr = r"show bgp ipv4 unicast regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        bgp_community: StrictStr = r"show bgp ipv4 unicast community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        ping: StrictStr = r"ping ipv4 {target} count 5 source {source}"
        traceroute: StrictStr = r"traceroute ipv4 {target} timeout 1 probe 2 source {source}"

    class IPv6(Command.IPv6):
        """Validation model for non-default ipv4 commands."""

        bgp_route: StrictStr = r"show bgp ipv6 unicast {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
        bgp_aspath: StrictStr = r"show bgp ipv6 unicast regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        bgp_community: StrictStr = r"show bgp ipv6 unicast community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        ping: StrictStr = r"ping ipv6 {target} count 5 source {source}"
        traceroute: StrictStr = r"traceroute ipv6 {target} timeout 1 probe 2 source {source}"

    class VPNIPv4(Command.VPNIPv4):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = r"show bgp vpnv4 unicast vrf {vrf} {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
        bgp_aspath: StrictStr = r"show bgp vpnv4 unicast vrf {vrf} regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        bgp_community: StrictStr = r"show bgp vpnv4 unicast vrf {vrf} community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        ping: StrictStr = r"ping vrf {vrf} {target} count 5 source {source}"
        traceroute: StrictStr = r"traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"

    class VPNIPv6(Command.VPNIPv6):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = r"show bgp vpnv6 unicast vrf {vrf} {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
        bgp_aspath: StrictStr = r"show bgp vpnv6 unicast vrf {vrf} regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        bgp_community: StrictStr = r"show bgp vpnv6 unicast vrf {vrf} community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
        ping: StrictStr = r"ping vrf {vrf} {target} count 5 source {source}"
        traceroute: StrictStr = r"traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class Juniper(Command):
    """Validation model for default juniper commands."""

    class IPv4(Command.IPv4):
        """Validation model for non-default dual afi commands."""

        bgp_route: StrictStr = "show route protocol bgp table inet.0 {target} detail"
        bgp_aspath: StrictStr = 'show route protocol bgp table inet.0 aspath-regex "{target}"'
        bgp_community: StrictStr = "show route protocol bgp table inet.0 community {target}"
        ping: StrictStr = "ping inet {target} count 5 source {source}"
        traceroute: StrictStr = "traceroute inet {target} wait 1 source {source}"

    class IPv6(Command.IPv6):
        """Validation model for non-default ipv4 commands."""

        bgp_route: StrictStr = "show route protocol bgp table inet6.0 {target} detail"
        bgp_aspath: StrictStr = 'show route protocol bgp table inet6.0 aspath-regex "{target}"'
        bgp_community: StrictStr = "show route protocol bgp table inet6.0 community {target}"
        ping: StrictStr = "ping inet6 {target} count 5 source {source}"
        traceroute: StrictStr = "traceroute inet6 {target} wait 1 source {source}"

    class VPNIPv4(Command.VPNIPv4):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = "show route protocol bgp table {vrf}.inet.0 {target} detail"
        bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}"'
        bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet.0 community {target}"
        ping: StrictStr = "ping inet routing-instance {vrf} {target} count 5 source {source}"
        traceroute: StrictStr = "traceroute inet routing-instance {vrf} {target} wait 1 source {source}"

    class VPNIPv6(Command.VPNIPv6):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = "show route protocol bgp table {vrf}.inet6.0 {target} detail"
        bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}"'
        bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet6.0 community {target}"
        ping: StrictStr = "ping inet6 routing-instance {vrf} {target} count 5 source {source}"
        traceroute: StrictStr = "traceroute inet6 routing-instance {vrf} {target} wait 1 source {source}"

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class Huawei(Command):
    """Validation model for default huawei commands."""

    class IPv4(Command.IPv4):
        """Default commands for ipv4 commands."""

        bgp_community: StrictStr = "display bgp routing-table regular-expression {target}"
        bgp_aspath: StrictStr = "display bgp routing-table regular-expression {target}"
        bgp_route: StrictStr = "display bgp routing-table {target}"
        ping: StrictStr = "ping -c 5 -a {source} {target}"
        traceroute: StrictStr = "tracert -q 2 -f 1 -a {source} {target}"

    class IPv6(Command.IPv6):
        """Default commands for ipv6 commands."""

        bgp_community: StrictStr = "display bgp ipv6 routing-table community {target}"
        bgp_aspath: StrictStr = "display bgp ipv6 routing-table regular-expression {target}"
        bgp_route: StrictStr = "display bgp ipv6 routing-table {target}"
        ping: StrictStr = "ping ipv6 -c 5 -a {source} {target}"
        traceroute: StrictStr = "tracert ipv6 -q 2 -f 1 -a {source} {target}"

    class VPNIPv4(Command.VPNIPv4):
        """Default commands for dual afi commands."""

        bgp_community: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
        bgp_aspath: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
        bgp_route: StrictStr = "display bgp vpnv4 vpn-instance {vrf} routing-table {target}"
        ping: StrictStr = "ping -vpn-instance {vrf} -c 5 -a {source} {target}"
        traceroute: StrictStr = "tracert -q 2 -f 1 -vpn-instance {vrf} -a {source} {target}"

    class VPNIPv6(Command.VPNIPv6):
        """Default commands for dual afi commands."""

        bgp_community: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
        bgp_aspath: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
        bgp_route: StrictStr = "display bgp vpnv6 vpn-instance {vrf} routing-table {target}"
        ping: StrictStr = "ping vpnv6 vpn-instance {vrf} -c 5 -a {source} {target}"
        traceroute: StrictStr = "tracert -q 2 -f 1 vpn-instance {vrf} -a {source} {target}"

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class Arista(Command):
    """Validation model for non-default commands."""

    class IPv4(Command.IPv4):
        """Validation model for non-default dual afi commands."""

        bgp_route: StrictStr = "show ip bgp {target}"
        bgp_aspath: StrictStr = "show ip bgp regexp {target}"
        bgp_community: StrictStr = "show ip bgp community {target}"
        ping: StrictStr = "ping ip {target} source {source}"
        traceroute: StrictStr = "traceroute ip {target} source {source}"

    class IPv6(Command.IPv6):
        """Validation model for non-default ipv4 commands."""

        bgp_route: StrictStr = "show ipv6 bgp {target}"
        bgp_aspath: StrictStr = "show ipv6 bgp regexp {target}"
        bgp_community: StrictStr = "show ipv6 bgp community {target}"
        ping: StrictStr = "ping ipv6 {target} source {source}"
        traceroute: StrictStr = "traceroute ipv6 {target} source {source}"

    class VPNIPv4(Command.VPNIPv4):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = "show ip bgp {target} vrf {vrf}"
        bgp_aspath: StrictStr = "show ip bgp regexp {target} vrf {vrf}"
        bgp_community: StrictStr = "show ip bgp community {target} vrf {vrf}"
        ping: StrictStr = "ping vrf {vrf} ip {target} source {source}"
        traceroute: StrictStr = "traceroute vrf {vrf} ip {target} source {source}"

    class VPNIPv6(Command.VPNIPv6):
        """Validation model for non-default ipv6 commands."""

        bgp_route: StrictStr = "show ipv6 bgp {target} vrf {vrf}"
        bgp_aspath: StrictStr = "show ipv6 bgp regexp {target} vrf {vrf}"
        bgp_community: StrictStr = "show ipv6 bgp community {target} vrf {vrf}"
        ping: StrictStr = "ping vrf {vrf} ipv6 {target} source {source}"
        traceroute: StrictStr = "traceroute vrf {vrf} ipv6 {target} source {source}"

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


_NOS_MAP = {
    "juniper": Juniper,
    "cisco_ios": CiscoIOS,
    "cisco_xr": CiscoXR,
    "huawei": Huawei,
    "arista": Arista,
}


class Commands(HyperglassModel):
    """Base class for command definitions."""

    cisco_ios: Command = CiscoIOS()
    cisco_xr: Command = CiscoXR()
    juniper: Command = Juniper()
    huawei: Command = Huawei()
    arista: Command = Arista()

    @classmethod
    def import_params(cls, input_params):
        """Import loaded YAML, initialize per-command definitions.

        Dynamically set attributes for the command class.

        Arguments:
            input_params {dict} -- Unvalidated command definitions

        Returns:
            {object} -- Validated commands object
        """
        obj = Commands()
        for nos, cmds in input_params.items():
            nos_cmd_set = _NOS_MAP.get(nos)
            nos_cmds = nos_cmd_set(**cmds)
            setattr(obj, nos, nos_cmds)
        return obj

    class Config:
        """Override pydantic config."""

        validate_all = False
