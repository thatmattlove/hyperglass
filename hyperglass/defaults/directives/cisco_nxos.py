"""Default Cisco NX-OS Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

__all__ = (
    "CiscoNXOS_BGPASPath",
    "CiscoNXOS_BGPCommunity",
    "CiscoNXOS_BGPRoute",
    "CiscoNXOS_Ping",
    "CiscoNXOS_Traceroute",
)

CiscoNXOS_BGPRoute = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="show bgp ipv4 unicast {target}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="show bgp ipv6 unicast {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_nxos"],
)

CiscoNXOS_BGPASPath = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                'show bgp ipv4 unicast regexp "{target}"',
                'show bgp ipv6 unicast regexp "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["cisco_nxos"],
)

CiscoNXOS_BGPCommunity = BuiltinDirective(
    id="__hyperglass_cisco_nxos_bgp_community__",
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
    platforms=["cisco_nxos"],
)

CiscoNXOS_Ping = BuiltinDirective(
    id="__hyperglass_cisco_nxos_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ping {target} source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ping6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_nxos"],
)

CiscoNXOS_Traceroute = BuiltinDirective(
    id="__hyperglass_cisco_nxos_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="traceroute {target} source {source4}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="traceroute6 {target} source {source6}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["cisco_nxos"],
)
