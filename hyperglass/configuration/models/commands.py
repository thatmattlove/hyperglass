"""Validate command configuration variables."""

# Disable string length warnings so I can actually read these commands
# flake8: noqa: E501

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Command(HyperglassModel):
    """Class model for non-default commands"""

    class IPv4(HyperglassModel):
        """Class model for non-default dual afi commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class IPv6(HyperglassModel):
        """Class model for non-default ipv4 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv4(HyperglassModel):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv6(HyperglassModel):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class Commands(HyperglassModel):
    """Base class for commands class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, dynamically sets
        attributes for the commands class.
        """
        obj = Commands()
        for (nos, cmds) in input_params.items():
            setattr(Commands, nos, Command(**cmds))
        return obj

    class CiscoIOS(Command):
        """Class model for default cisco_ios commands"""

        class VPNIPv4(Command.VPNIPv4):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vpnv4 unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp vpnv4 unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp vpnv4 unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
            )

        class VPNIPv6(Command.VPNIPv6):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vpnv6 unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp vpnv6 unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp vpnv6 unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
            )

        class IPv4(Command.IPv4):
            """Default commands for ipv4 commands"""

            bgp_community: str = "show bgp ipv4 unicast community {target}"
            bgp_aspath: str = 'show bgp ipv4 unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
            ping: str = "ping {target} repeat 5 source {source}"
            traceroute: str = "traceroute {target} timeout 1 probe 2 source {source}"

        class IPv6(Command.IPv6):
            """Default commands for ipv6 commands"""

            bgp_community: str = "show bgp ipv6 unicast community {target}"
            bgp_aspath: str = 'show bgp ipv6 unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
            ping: str = ("ping ipv6 {target} repeat 5 source {source}")
            traceroute: str = (
                "traceroute ipv6 {target} timeout 1 probe 2 source {source}"
            )

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    class CiscoXR(Command):
        """Class model for default cisco_xr commands"""

        class IPv4(Command.IPv4):
            """Class model for non-default dual afi commands"""

            bgp_route: str = r"show bgp ipv4 unicast {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            bgp_aspath: str = r"show bgp ipv4 unicast regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            bgp_community: str = r"show bgp ipv4 unicast community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            ping: str = r"ping ipv4 {target} count 5 source {source}"
            traceroute: str = r"traceroute ipv4 {target} timeout 1 probe 2 source {source}"

        class IPv6(Command.IPv6):
            """Class model for non-default ipv4 commands"""

            bgp_route: str = r"show bgp ipv6 unicast {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            bgp_aspath: str = r"show bgp ipv6 unicast regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            bgp_community: str = r"show bgp ipv6 unicast community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            ping: str = r"ping ipv6 {target} count 5 source {source}"
            traceroute: str = r"traceroute ipv6 {target} timeout 1 probe 2 source {source}"

        class VPNIPv4(Command.VPNIPv4):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = r"show bgp vpnv4 unicast vrf {vrf} {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            bgp_aspath: str = r"show bgp vpnv4 unicast vrf {vrf} regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            bgp_community: str = r"show bgp vpnv4 unicast vrf {vrf} community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            ping: str = r"ping vrf {vrf} {target} count 5 source {source}"
            traceroute: str = r"traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"

        class VPNIPv6(Command.VPNIPv6):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = r"show bgp vpnv6 unicast vrf {vrf} {target} | util egrep \\(BGP routing table entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            bgp_aspath: str = r"show bgp vpnv6 unicast vrf {vrf} regexp {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            bgp_community: str = r"show bgp vpnv6 unicast vrf {vrf} community {target} | utility egrep -v \\(BGP |Table |Non-stop\\)"
            ping: str = r"ping vrf {vrf} {target} count 5 source {source}"
            traceroute: str = r"traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    class Juniper(Command):
        """Class model for default juniper commands"""

        class IPv4(Command.IPv4):
            """Class model for non-default dual afi commands"""

            bgp_route: str = "show route protocol bgp table inet.0 {target} detail"
            bgp_aspath: str = "show route protocol bgp table inet.0 aspath-regex {target}"
            bgp_community: str = "show route protocol bgp table inet.0 community {target}"
            ping: str = "ping inet {target} count 5 source {source}"
            traceroute: str = "traceroute inet {target} wait 1 source {source}"

        class IPv6(Command.IPv6):
            """Class model for non-default ipv4 commands"""

            bgp_route: str = "show route protocol bgp table inet6.0 {target} detail"
            bgp_aspath: str = "show route protocol bgp community {target}"
            bgp_community: str = "show route protocol bgp aspath-regex {target}"
            ping: str = "ping inet6 {target} count 5 source {source}"
            traceroute: str = "traceroute inet6 {target} wait 1 source {source}"

        class VPNIPv4(Command.VPNIPv4):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = "show route protocol bgp table {vrf} {target} detail"
            bgp_aspath: str = "show route protocol bgp table {vrf} aspath-regex {target}"
            bgp_community: str = "show route protocol bgp table {vrf} community {target}"
            ping: str = "ping inet routing-instance {vrf} {target} count 5 source {source}"
            traceroute: str = "traceroute inet routing-instance {vrf} {target} wait 1 source {source}"

        class VPNIPv6(Command.VPNIPv6):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = "show route protocol bgp table {vrf} {target} detail"
            bgp_aspath: str = "show route protocol bgp table {vrf} aspath-regex {target}"
            bgp_community: str = "show route protocol bgp table {vrf} community {target}"
            ping: str = "ping inet6 routing-instance {vrf} {target} count 5 source {source}"
            traceroute: str = "traceroute inet6 routing-instance {vrf} {target} wait 1 source {source}"

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    class Huawei(Command):
        """Class model for default huawei commands"""

        class IPv4(Command.IPv4):
            """Default commands for ipv4 commands"""

            bgp_community: str = "display bgp routing-table regular-expression {target}"
            bgp_aspath: str = "display bgp routing-table regular-expression {target}"
            bgp_route: str = "display bgp routing-table {target}"
            ping: str = "ping -c 5 -a {source} {target}"
            traceroute: str = "tracert -q 2 -f 1 -a {source} {target}"

        class IPv6(Command.IPv6):
            """Default commands for ipv6 commands"""

            bgp_community: str = "display bgp ipv6 routing-table community {target}"
            bgp_aspath: str = "display bgp ipv6 routing-table regular-expression {target}"
            bgp_route: str = "display bgp ipv6 routing-table {target}"
            ping: str = "ping ipv6 -c 5 -a {source} {target}"
            traceroute: str = "tracert ipv6 -q 2 -f 1 -a {source} {target}"

        class VPNIPv4(Command.VPNIPv4):
            """Default commands for dual afi commands"""

            bgp_community: str = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
            bgp_aspath: str = "display bgp vpnv4 vpn-instance {vrf} routing-table regular-expression {target}"
            bgp_route: str = "display bgp vpnv4 vpn-instance {vrf} routing-table {target}"
            ping: str = "ping -vpn-instance {vrf} -c 5 -a {source} {target}"
            traceroute: str = "tracert -q 2 -f 1 -vpn-instance {vrf} -a {source} {target}"

        class VPNIPv6(Command.VPNIPv6):
            """Default commands for dual afi commands"""

            bgp_community: str = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
            bgp_aspath: str = "display bgp vpnv6 vpn-instance {vrf} routing-table regular-expression {target}"
            bgp_route: str = "display bgp vpnv6 vpn-instance {vrf} routing-table {target}"
            ping: str = "ping vpnv6 vpn-instance {vrf} -c 5 -a {source} {target}"
            traceroute: str = "tracert -q 2 -f 1 vpn-instance {vrf} -a {source} {target}"

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    class Arista(Command):
        """Class model for non-default commands"""

        class IPv4(Command.IPv4):
            """Class model for non-default dual afi commands"""

            bgp_route: str = "show ip bgp {target}"
            bgp_aspath: str = "show ip bgp regexp {target}"
            bgp_community: str = "show ip bgp community {target}"
            ping: str = "ping ip {target} source {source}"
            traceroute: str = "traceroute ip {target} source {source}"

        class IPv6(Command.IPv6):
            """Class model for non-default ipv4 commands"""

            bgp_route: str = "show ipv6 bgp {target}"
            bgp_aspath: str = "show ipv6 bgp regexp {target}"
            bgp_community: str = "show ipv6 bgp community {target}"
            ping: str = "ping ipv6 {target} source {source}"
            traceroute: str = "traceroute ipv6 {target} source {source}"

        class VPNIPv4(Command.VPNIPv4):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = "show ip bgp {target} vrf {vrf}"
            bgp_aspath: str = "show ip bgp regexp {target} vrf {vrf}"
            bgp_community: str = "show ip bgp community {target} vrf {vrf}"
            ping: str = "ping vrf {vrf} ip {target} source {source}"
            traceroute: str = "traceroute vrf {vrf} ip {target} source {source}"

        class VPNIPv6(Command.VPNIPv6):
            """Class model for non-default ipv6 commands"""

            bgp_route: str = "show ipv6 bgp {target} vrf {vrf}"
            bgp_aspath: str = "show ipv6 bgp regexp {target} vrf {vrf}"
            bgp_community: str = "show ipv6 bgp community {target} vrf {vrf}"
            ping: str = "ping vrf {vrf} ipv6 {target} source {source}"
            traceroute: str = "traceroute vrf {vrf} ipv6 {target} source {source}"

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    cisco_ios: Command = CiscoIOS()
    cisco_xr: Command = CiscoXR()
    juniper: Command = Juniper()
    huawei: Command = Huawei()
    arista: Command = Arista()

    class Config:
        """Pydantic Config Overrides"""

        validate_all = False
