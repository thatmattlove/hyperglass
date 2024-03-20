"""Default TNSR Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "TNSR_BGPASPath",
    "TNSR_BGPCommunity",
    "TNSR_BGPRoute",
    "TNSR_Ping",
    "TNSR_Traceroute",
)

NAME = "TNSR"
PLATFORMS = ["tnsr"]

TNSR_BGPRoute = BuiltinDirective(
    id="__hyperglass_tnsr_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command='dataplane shell sudo vtysh -c "show bgp ipv4 unicast {target}"',
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command='dataplane shell sudo vtysh -c "show bgp ipv6 unicast {target}"',
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

TNSR_BGPASPath = BuiltinDirective(
    id="__hyperglass_tnsr_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'dataplane shell sudo vtysh -c "show bgp ipv4 unicast regexp {target}"',
                'dataplane shell sudo vtysh -c "show bgp ipv6 unicast regexp {target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

TNSR_BGPCommunity = BuiltinDirective(
    id="__hyperglass_tnsr_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'dataplane shell sudo vtysh -c "show bgp ipv4 unicast community {target}"',
                'dataplane shell sudo vtysh -c "show bgp ipv6 unicast community {target}"',
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

TNSR_Ping = BuiltinDirective(
    id="__hyperglass_tnsr_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} ipv4 source {source4} count 5 timeout 1",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping {target} ipv6 source {source6} count 5 timeout 1",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

TNSR_Traceroute = BuiltinDirective(
    id="__hyperglass_tnsr_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute {target} ipv4 source {source4} timeout 1 waittime 1",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="traceroute {target} ipv6 source {source6} timeout 1 waittime 1",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
