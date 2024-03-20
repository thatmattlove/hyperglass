"""Default Cisco NX-OS Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "CiscoNXOS_BGPASPath",
    "CiscoNXOS_BGPCommunity",
    "CiscoNXOS_BGPRoute",
    "CiscoNXOS_Ping",
    "CiscoNXOS_Traceroute",
)

NAME = "Cisco NX-OS"
PLATFORMS = ["cisco_nxos"]

CiscoNXOS_BGPRoute = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="show bgp ipv4 unicast {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="show bgp ipv6 unicast {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

CiscoNXOS_BGPASPath = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show bgp ipv4 unicast regexp "{target}"',
                'show bgp ipv6 unicast regexp "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

CiscoNXOS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "show bgp ipv4 unicast community {target}",
                "show bgp ipv6 unicast community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)

CiscoNXOS_Ping = BuiltinDirective(
    id="__hyperglass_cisco_nxos_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

CiscoNXOS_Traceroute = BuiltinDirective(
    id="__hyperglass_cisco_nxos_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute {target} source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="traceroute6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
