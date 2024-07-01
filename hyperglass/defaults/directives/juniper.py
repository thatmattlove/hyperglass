"""Default Juniper Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "JuniperBGPRoute",
    "JuniperBGPASPath",
    "JuniperBGPCommunity",
    "JuniperPing",
    "JuniperTraceroute",
    "JuniperBGPRouteTable",
    "JuniperBGPASPathTable",
    "JuniperBGPCommunityTable",
)

NAME = "Juniper Junos"
PLATFORMS = ["juniper", "juniper_junos"]

JuniperBGPRoute = BuiltinDirective(
    id="__hyperglass_juniper_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="show route protocol bgp table inet.0 {target} detail",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="show route protocol bgp table inet6.0 {target} detail",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    table_output="__hyperglass_juniper_bgp_route_table__",
    platforms=PLATFORMS,
)

JuniperBGPASPath = BuiltinDirective(
    id="__hyperglass_juniper_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show route protocol bgp table inet.0 aspath-regex "{target}"',
                'show route protocol bgp table inet6.0 aspath-regex "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    table_output="__hyperglass_juniper_bgp_aspath_table__",
    platforms=PLATFORMS,
)

JuniperBGPCommunity = BuiltinDirective(
    id="__hyperglass_juniper_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show route protocol bgp table inet.0 community "{target}" detail',
                'show route protocol bgp table inet6.0 community "{target}" detail',
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    table_output="__hyperglass_juniper_bgp_community_table__",
    platforms=PLATFORMS,
)


JuniperPing = BuiltinDirective(
    id="__hyperglass_juniper_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping inet {target} count 5 source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping inet6 {target} count 5 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

JuniperTraceroute = BuiltinDirective(
    id="__hyperglass_juniper_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute inet {target} wait 1 source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="traceroute inet6 {target} wait 2 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

# Table Output Directives

JuniperBGPRouteTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_route_table__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="show route protocol bgp table inet.0 {target} best detail | display xml",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="show route protocol bgp table inet6.0 {target} best detail | display xml",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

JuniperBGPASPathTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_aspath_table__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show route protocol bgp table inet.0 aspath-regex "{target}" detail | display xml',
                'show route protocol bgp table inet6.0 aspath-regex "{target}" detail | display xml',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

JuniperBGPCommunityTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_community_table__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "show route protocol bgp table inet.0 community {target} detail | display xml",
                "show route protocol bgp table inet6.0 community {target} detail | display xml",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)
