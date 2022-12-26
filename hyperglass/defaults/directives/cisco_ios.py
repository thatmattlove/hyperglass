"""Default Cisco IOS Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

__all__ = (
    "CiscoIOS_BGPASPath",
    "CiscoIOS_BGPCommunity",
    "CiscoIOS_BGPRoute",
    "CiscoIOS_Ping",
    "CiscoIOS_Traceroute",
)

CiscoIOS_BGPRoute = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show bgp ipv4 unicast {target} | exclude pathid:|Epoch",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show bgp ipv6 unicast {target} | exclude pathid:|Epoch",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_ios"],
)

CiscoIOS_BGPASPath = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                'show bgp ipv4 unicast quote-regexp "{target}"',
                'show bgp ipv6 unicast quote-regexp "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["cisco_ios"],
)

CiscoIOS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_cisco_ios_bgp_community__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "show bgp ipv4 unicast community {target}",
                "show bgp ipv6 unicast community {target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=["cisco_ios"],
)

CiscoIOS_Ping = BuiltinDirective(
    id="__hyperglass_cisco_ios_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} repeat 5 source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ping ipv6 {target} repeat 5 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_ios"],
)

CiscoIOS_Traceroute = BuiltinDirective(
    id="__hyperglass_cisco_ios_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute {target} timeout 1 probe 2 source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="traceroute ipv6 {target} timeout 1 probe 2 source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_ios"],
)
