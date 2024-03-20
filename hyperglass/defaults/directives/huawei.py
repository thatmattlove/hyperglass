"""Default Huawei Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "Huawei_BGPASPath",
    "Huawei_BGPCommunity",
    "Huawei_BGPRoute",
    "Huawei_Ping",
    "Huawei_Traceroute",
)

NAME = "Huawei VRP"
PLATFORMS = ["huawei", "huawei_vrpv8"]

Huawei_BGPRoute = BuiltinDirective(
    id="__hyperglass_huawei_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="display bgp routing-table {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="display bgp ipv6 routing-table {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

Huawei_BGPASPath = BuiltinDirective(
    id="__hyperglass_huawei_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "display bgp routing-table regular-expression {target}",
                "display bgp ipv6 routing-table regular-expression {target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

Huawei_BGPCommunity = BuiltinDirective(
    id="__hyperglass_huawei_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "display bgp routing-table community {target}",
                "display bgp ipv6 routing-table community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

Huawei_Ping = BuiltinDirective(
    id="__hyperglass_huawei_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping -c 5 -a {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping ipv6 -c 5 -a {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

Huawei_Traceroute = BuiltinDirective(
    id="__hyperglass_huawei_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="tracert -q 2 -f 1 -a {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="tracert -q 2 -f 1 -a {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
