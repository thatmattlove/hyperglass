"""Default Juniper Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

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

JuniperBGPRoute = BuiltinDirective(
    id="__hyperglass_juniper_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show route protocol table inet.0 {target} detail",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show route protocol table inet6.0 {target} detail",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["juniper"],
)

JuniperBGPASPath = BuiltinDirective(
    id="__hyperglass_juniper_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                'show route protocol table inet.0 aspath-regex "{target}"',
                'show route protocol table inet6.0 aspath-regex "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["juniper"],
)

JuniperBGPCommunity = BuiltinDirective(
    id="__hyperglass_juniper_bgp_community__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                'show route protocol table inet.0 community "{target}" detail',
                'show route protocol table inet6.0 community "{target}" detail',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["juniper"],
)


JuniperPing = BuiltinDirective(
    id="__hyperglass_juniper_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ping inet {target} count 5 source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ping inet6 {target} count 5 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["juniper"],
)

JuniperTraceroute = BuiltinDirective(
    id="__hyperglass_juniper_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute inet {target} wait 1 source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="traceroute inet6 {target} wait 1 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["juniper"],
)

# Table Output Directives

JuniperBGPRouteTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_route_table__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show route protocol bgp table inet.0 {target} best detail | display xml",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show route protocol bgp table inet6.0 {target} best detail | display xml",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    table_output=True,
    platforms=["juniper"],
)

JuniperBGPASPathTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_aspath_table__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                'show route protocol bgp table inet.0 aspath-regex "{target}" detail | display xml',
                'show route protocol bgp table inet6.0 aspath-regex "{target}" detail | display xml',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    table_output=True,
    platforms=["juniper"],
)

JuniperBGPCommunityTable = BuiltinDirective(
    id="__hyperglass_juniper_bgp_community_table__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show route protocol bgp table inet.0 community {target} detail | display xml",
                "show route protocol bgp table inet6.0 community {target} detail | display xml",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    table_output=True,
    platforms=["juniper"],
)
