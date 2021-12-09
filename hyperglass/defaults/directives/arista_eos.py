"""Default Arista Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

__all__ = (
    "AristaBGPRoute",
    "AristaBGPASPath",
    "AristaBGPCommunity",
    "AristaPing",
    "AristaTraceroute",
    "AristaBGPRouteTable",
    "AristaBGPASPathTable",
    "AristaBGPCommunityTable",
)

AristaBGPRoute = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show ip bgp {target}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show ipv6 bgp {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    table_output="__hyperglass_arista_eos_bgp_route_table__",
    platforms=["arista_eos"],
)

AristaBGPASPath = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show ip bgp regexp {target}",
                "show ipv6 bgp regexp {target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    table_output="__hyperglass_arista_eos_bgp_aspath_table__",
    platforms=["arista_eos"],
)

AristaBGPCommunity = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_community__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show ip bgp community {target}",
                "show ipv6 bgp community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    table_output="__hyperglass_arista_eos_bgp_community_table__",
    platforms=["arista_eos"],
)


AristaPing = BuiltinDirective(
    id="__hyperglass_arista_eos_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ping ip {target} source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ping ipv6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["arista_eos"],
)

AristaTraceroute = BuiltinDirective(
    id="__hyperglass_arista_eos_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute ip {target} source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="traceroute ipv6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["arista_eos"],
)

# Table Output Directives

AristaBGPRouteTable = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_route_table__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show ip bgp {target} | json",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show ipv6 bgp {target} | json",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["arista_eos"],
)

AristaBGPASPathTable = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_aspath_table__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show ip bgp regexp {target} | json",
                "show ipv6 bgp regexp {target} | json",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["arista_eos"],
)

AristaBGPCommunityTable = BuiltinDirective(
    id="__hyperglass_arista_eos_bgp_community_table__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show ip bgp community {target} | json",
                "show ipv6 bgp community {target} | json",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=["arista_eos"],
)
