"""Default VyOS Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "VyOS_BGPASPath",
    "VyOS_BGPCommunity",
    "VyOS_BGPRoute",
    "VyOS_Ping",
    "VyOS_Traceroute",
)

NAME = "VyOS"
PLATFORMS = ["vyos"]

VyOS_BGPRoute = BuiltinDirective(
    id="__hyperglass_vyos_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="show ip bgp {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="show ipv6 bgp {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

VyOS_BGPASPath = BuiltinDirective(
    id="__hyperglass_vyos_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show ip bgp regexp "{target}"',
                'show ipv6 bgp regexp "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

VyOS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_vyos_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "show ip bgp community {target}",
                "show ipv6 bgp community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

VyOS_Ping = BuiltinDirective(
    id="__hyperglass_vyos_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} count 5 interface {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping {target} count 5 interface {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

VyOS_Traceroute = BuiltinDirective(
    id="__hyperglass_vyos_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="mtr -4 -G 1 -c 1 -w -o SAL -a {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="mtr -6 -G 1 -c 1 -w -o SAL -a {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
