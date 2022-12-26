"""Default Nokia SR-OS Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

__all__ = (
    "NokiaSROS_BGPASPath",
    "NokiaSROS_BGPCommunity",
    "NokiaSROS_BGPRoute",
    "NokiaSROS_Ping",
    "NokiaSROS_Traceroute",
)

NokiaSROS_BGPRoute = BuiltinDirective(
    id="__hyperglass_nokia_sros_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="/show router bgp routes {target} ipv4 hunt",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="/show router bgp routes {target} ipv6 hunt",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["nokia_sros"],
)

NokiaSROS_BGPASPath = BuiltinDirective(
    id="__hyperglass_nokia_sros_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "/show router bgp routes aspath-regex {target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["nokia_sros"],
)

NokiaSROS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_nokia_sros_bgp_community__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "/show router bgp routes community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=["nokia_sros"],
)

NokiaSROS_Ping = BuiltinDirective(
    id="__hyperglass_nokia_sros_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="/ping {target} source-address {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="/ping {target} source-address {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["nokia_sros"],
)

NokiaSROS_Traceroute = BuiltinDirective(
    id="__hyperglass_nokia_sros_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="/traceroute {target} source-address {source4} wait 2 seconds",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="/traceroute {target} source-address {source6} wait 2 seconds",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["nokia_sros"],
)
