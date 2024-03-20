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
    "FRRouting_BGPASPath",
    "FRRouting_BGPCommunity",
    "FRRouting_BGPRoute",
    "FRRouting_Ping",
    "FRRouting_Traceroute",
)

NAME = "FRRouting"
PLATFORMS = ["frr"]

FRRouting_BGPRoute = BuiltinDirective(
    id="__hyperglass_frr_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command='vtysh -c "show bgp ipv4 unicast {target}"',
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command='vtysh -c "show bgp ipv6 unicast {target}"',
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

FRRouting_BGPASPath = BuiltinDirective(
    id="__hyperglass_frr_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'vtysh -c "show bgp ipv4 unicast regexp {target}"',
                'vtysh -c "show bgp ipv6 unicast regexp {target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

FRRouting_BGPCommunity = BuiltinDirective(
    id="__hyperglass_frr_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'vtysh -c "show bgp ipv4 unicast community {target}"',
                'vtysh -c "show bgp ipv6 unicast community {target}"',
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

FRRouting_Ping = BuiltinDirective(
    id="__hyperglass_frr_ping__",
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

FRRouting_Traceroute = BuiltinDirective(
    id="__hyperglass_frr_traceroute__",
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
