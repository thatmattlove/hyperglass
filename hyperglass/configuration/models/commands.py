"""
Defines models for all config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Third Party Imports
from pydantic import BaseSettings


class Command(BaseSettings):
    """Class model for non-default commands"""

    class IPv4(BaseSettings):
        """Class model for non-default dual afi commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class IPv6(BaseSettings):
        """Class model for non-default ipv4 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv4(BaseSettings):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv6(BaseSettings):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    ipv4: IPv4 = IPv4()
    ipv6: IPv6 = IPv6()
    vpn_ipv4: VPNIPv4 = VPNIPv4()
    vpn_ipv6: VPNIPv6 = VPNIPv6()


class Commands(BaseSettings):
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

    class CiscoIOS(BaseSettings):
        """Class model for default cisco_ios commands"""

        class IPv4Vrf(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vpnv4 unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp vpnv4 unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp vpnv4 unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
            )

        class IPv6Vrf(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vpnv6 unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp vpnv6 unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp vpnv6 unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source}"
            )

        class IPv4Default(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_community: str = "show bgp ipv4 unicast community {target}"
            bgp_aspath: str = 'show bgp ipv4 unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
            ping: str = "ping {target} repeat 5 source {source}"
            traceroute: str = "traceroute {target} timeout 1 probe 2 source {source}"

        class IPv6Default(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_community: str = "show bgp ipv6 unicast community {target}"
            bgp_aspath: str = 'show bgp ipv6 unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
            ping: str = ("ping {afi} {target} repeat 5 source {source}")
            traceroute: str = (
                "traceroute ipv6 {target} timeout 1 probe 2 source {source}"
            )

        ipv4_default: IPv4Default = IPv4Default()
        ipv6_default: IPv6Default = IPv6Default()
        ipv4_vrf: IPv4Vrf = IPv4Vrf()
        ipv6_vrf: IPv6Vrf = IPv6Vrf()

    class CiscoXR(BaseSettings):
        """Class model for default cisco_xr commands"""

        class Dual(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = (
                "show bgp all unicast community {target} | utility egrep -v "
                '"\\(BGP |Table |Non-stop\\)"'
            )
            bgp_aspath: str = (
                "show bgp all unicast regexp {target} | utility egrep -v "
                '"\\(BGP |Table |Non-stop\\)"'
            )

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_route: str = (
                "show bgp ipv4 unicast {target} | util egrep \\(BGP routing table "
                "entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            )
            ping: str = "ping ipv4 {target} count 5 source {src_addr_ipv4}"
            traceroute: str = (
                "traceroute ipv4 {target} timeout 1 probe 2 source {source}"
            )

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_route: str = (
                "show bgp ipv6 unicast {target} | util egrep \\(BGP routing table "
                "entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            )
            ping: str = "ping ipv6 {target} count 5 source {src_addr_ipv6}"
            traceroute: str = (
                "traceroute ipv6 {target} timeout 1 probe 2 source {source}"
            )

        dual: Dual = Dual()
        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()

    class Juniper(BaseSettings):
        """Class model for default juniper commands"""

        class Dual(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community = "show route protocol bgp community {target}"
            bgp_aspath = "show route protocol bgp aspath-regex {target}"

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_route = "show route protocol bgp table inet.0 {target} detail"
            ping = "ping inet {target} count 5 source {src_addr_ipv4}"
            traceroute = "traceroute inet {target} wait 1 source {source}"

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_route = "show route protocol bgp table inet6.0 {target} detail"
            ping = "ping inet6 {target} count 5 source {src_addr_ipv6}"
            traceroute = "traceroute inet6 {target} wait 1 source {source}"

        dual: Dual = Dual()
        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()

    class Huawei(BaseSettings):
        """Class model for default huawei commands"""

        class IPv4Vrf(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = (
                "display bgp vpnv4 vpn-instance {vrf} routing-table "
                "regular-expression {target}"
            )
            bgp_aspath: str = (
                "display bgp vpnv4 vpn-instance {vrf} routing-table "
                "regular-expression {target}"
            )
            bgp_route: str = (
                "display bgp vpnv4 vpn-instance {vrf} routing-table {target}"
            )
            ping: str = "ping -vpn-instance {vrf} -c 5 -a {source} {target}"
            traceroute: str = (
                "tracert -q 2 -f 1 -vpn-instance {vrf} -a {source} {target}"
            )

        class IPv6Vrf(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = (
                "display bgp vpnv6 vpn-instance {vrf} routing-table "
                "regular-expression {target}"
            )
            bgp_aspath: str = (
                "display bgp vpnv6 vpn-instance {vrf} routing-table "
                "regular-expression {target}"
            )
            bgp_route: str = (
                "display bgp vpnv6 vpn-instance {vrf} routing-table {target}"
            )
            ping: str = "ping vpnv6 vpn-instance {vrf} -c 5 -a {source} {target}"
            traceroute: str = (
                "tracert -q 2 -f 1 vpn-instance {vrf} -a {source} {target}"
            )

        class IPv4Default(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_community: str = "display bgp routing-table regular-expression {target}"
            bgp_aspath: str = "display bgp routing-table regular-expression {target}"
            bgp_route: str = "display bgp routing-table {target}"
            ping: str = "ping -c 5 -a {source} {target}"
            traceroute: str = "tracert -q 2 -f 1 -a {source} {target}"

        class IPv6Default(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_community: str = "display bgp ipv6 routing-table community {target}"
            bgp_aspath: str = (
                "display bgp ipv6 routing-table regular-expression {target}"
            )
            bgp_route: str = "display bgp ipv6 routing-table {target}"
            ping: str = "ping ipv6 -c 5 -a {source} {target}"
            traceroute: str = "tracert ipv6 -q 2 -f 1 -a {source} {target}"

        ipv4_default: IPv4Default = IPv4Default()
        ipv6_default: IPv6Default = IPv6Default()
        ipv4_vrf: IPv4Vrf = IPv4Vrf()
        ipv6_vrf: IPv6Vrf = IPv6Vrf()

    cisco_ios: Command = CiscoIOS()
    cisco_xr: Command = CiscoXR()
    juniper: Command = Juniper()
    huawei: Command = Huawei()

    class Config:
        """Pydantic Config"""

        validate_all = False
        validate_assignment = True
