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

        class VPNv4IPv4(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp {afi} unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp {afi} unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp {afi} unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source} "
                "| exclude Type escape"
            )

        class VPNv6IPv6(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp {afi} unicast vrf {vrf} community {target}"
            bgp_aspath: str = 'show bgp {afi} unicast vrf {vrf} quote-regexp "{target}"'
            bgp_route: str = "show bgp {afi} unicast vrf {vrf} {target}"
            ping: str = "ping vrf {vrf} {target} repeat 5 source {source}"
            traceroute: str = (
                "traceroute vrf {vrf} {target} timeout 1 probe 2 source {source} "
                "| exclude Type escape"
            )

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_community: str = "show bgp {afi} unicast community {target}"
            bgp_aspath: str = 'show bgp {afi} unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp {afi} unicast {target} | exclude pathid:|Epoch"
            ping: str = "ping {target} repeat 5 source {source} | exclude Type escape"
            traceroute: str = (
                "traceroute {target} timeout 1 probe 2 source {source} "
                "| exclude Type escape"
            )

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_community: str = "show bgp {afi} unicast community {target}"
            bgp_aspath: str = 'show bgp {afi} unicast quote-regexp "{target}"'
            bgp_route: str = "show bgp {afi} unicast {target} | exclude pathid:|Epoch"
            ping: str = (
                "ping {afi} {target} repeat 5 source {source} | exclude Type escape"
            )
            traceroute: str = (
                "traceroute ipv6 {target} timeout 1 probe 2 source {source} "
                "| exclude Type escape"
            )

        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()
        vpn_ipv4: VPNv4IPv4 = VPNv4IPv4()
        vpn_ipv6: VPNv6IPv6 = VPNv6IPv6()

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

    cisco_ios: Command = CiscoIOS()
    cisco_xr: Command = CiscoXR()
    juniper: Command = Juniper()

    class Config:
        """Pydantic Config"""

        validate_all = False
        validate_assignment = True
