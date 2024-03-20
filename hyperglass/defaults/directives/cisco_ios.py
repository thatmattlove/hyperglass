"""Default Cisco IOS Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "CiscoIOS_BGPASPath",
    "CiscoIOS_BGPCommunity",
    "CiscoIOS_BGPRoute",
    "CiscoIOS_Ping",
    "CiscoIOS_Traceroute",
)

NAME = "Cisco IOS"
PLATFORMS = ["cisco_ios"]

CiscoIOS_BGPRoute = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="show bgp ipv4 unicast {target} | exclude pathid:|Epoch",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="show bgp ipv6 unicast {target} | exclude pathid:|Epoch",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

CiscoIOS_BGPASPath = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'show bgp ipv4 unicast quote-regexp "{target}"',
                'show bgp ipv6 unicast quote-regexp "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

CiscoIOS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_community__",
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

CiscoIOS_Ping = BuiltinDirective(
    id="__hyperglass_cisco_ios_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} repeat 5 source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping ipv6 {target} repeat 5 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

CiscoIOS_Traceroute = BuiltinDirective(
    id="__hyperglass_cisco_ios_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute {target} timeout 1 probe 2 source {source4}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="traceroute ipv6 {target} timeout 1 probe 2 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)
