"""Default FRRouting Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "OpenBGPD_BGPASPath",
    "OpenBGPD_BGPCommunity",
    "OpenBGPD_BGPRoute",
    "OpenBGPD_Ping",
    "OpenBGPD_Traceroute",
)

NAME = "OpenBGPD"
PLATFORMS = ["openbgpd"]

OpenBGPD_BGPRoute = BuiltinDirective(
    id="__hyperglass_openbgpd_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="bgpctl show rib inet {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="bgpctl show rib inet6 {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

OpenBGPD_BGPASPath = BuiltinDirective(
    id="__hyperglass_openbgpd_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "bgpctl show rib inet as {target}",
                "bgpctl show rib inet6 as {target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

OpenBGPD_BGPCommunity = BuiltinDirective(
    id="__hyperglass_openbgpd_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "bgpctl show rib inet community {target}",
                "bgpctl show rib inet6 community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

OpenBGPD_Ping = BuiltinDirective(
    id="__hyperglass_openbgpd_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping -4 -c 5 -I {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping -6 -c 5 -I {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

OpenBGPD_Traceroute = BuiltinDirective(
    id="__hyperglass_openbgpd_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute -4 -w 1 -q 1 -s {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="traceroute -6 -w 1 -q 1 -s {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
