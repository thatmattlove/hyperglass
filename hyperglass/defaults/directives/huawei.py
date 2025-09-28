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
    "HuaweiBGPRouteTable",
    "HuaweiBGPASPathTable",
    "HuaweiBGPCommunityTable",
)

NAME = "Huawei VRP"
PLATFORMS = ["huawei", "huawei_vrpv8"]

Huawei_BGPRoute = BuiltinDirective(
    id="__hyperglass_huawei_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            ge="8",
            le="32",
            action="permit",
            command="display bgp routing-table {target} | no-more",
        ),
        RuleWithIPv6(
            condition="::/0",
            ge="10",
            le="128",
            action="permit",
            command="display bgp ipv6 routing-table {target} | no-more",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    plugins=["bgp_route_huawei", "bgp_routestr_huawei"],
    table_output="__hyperglass_huawei_bgp_route_table__",
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
    table_output="__hyperglass_huawei_bgp_aspath_table__",
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
    table_output="__hyperglass_huawei_bgp_community_table__",
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
            command="tracert -w 500 -q 1 -f 1 -a {source4} {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="tracert ipv6 -w 500 -q 1 -f 1 -a {source6} {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

# Table Output Directives

HuaweiBGPRouteTable = BuiltinDirective(
    id="__hyperglass_huawei_bgp_route_table__",
    name="BGP Route",
    rules=[
        # Regra DENY RFC 6598
        RuleWithIPv4(
            condition="100.64.0.0/10",
            ge="10",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY RFC 1918 CLASSE A
        RuleWithIPv4(
            condition="10.0.0.0/8",
            ge="8",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY RFC 1918 CLASSE B
        RuleWithIPv4(
            condition="172.16.0.0/12",
            ge="12",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY RFC 1918 classe C
        RuleWithIPv4(
            condition="192.168.0.0/16",
            ge="16",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY LO
        RuleWithIPv4(
            condition="127.0.0.0/8",
            ge="8",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY DEFAULT
        RuleWithIPv4(
            condition="0.0.0.0/8",
            ge="8",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY AS PREFIXO
        # RuleWithIPv4(
        #    condition="x.x.x.x/xx",
        #    ge="xx",
        #    le="32",
        #    action="deny",
        #    command="",
        # ),
        RuleWithIPv4(
            condition="0.0.0.0/0",
            ge="8",
            le="32",
            action="permit",
            command="display bgp routing-table {target} | no-more",
        ),
        # REGRA DENY SITE LOCAL DEPRECIADO RFC 3879
        RuleWithIPv6(
            condition="fec0::/10",
            ge="10",
            le="128",
            action="deny",
            command="",
        ),
        # REGRA DENY ULA RFC 4193
        RuleWithIPv6(
            condition="fc00::/7",
            ge="7",
            le="128",
            action="deny",
            command="",
        ),
        # REGRA DENY LINK LOCAL RFC 4291
        RuleWithIPv6(
            condition="fe80::/10",
            ge="10",
            le="128",
            action="deny",
            command="",
        ),
        # REGRA DENY Unspecified RFC 4291
        RuleWithIPv6(
            condition="::/128",
            ge="128",
            le="128",
            action="deny",
            command="",
        ),
        # REGRA DENY LO RFC 4291
        RuleWithIPv6(
            condition="::1/128",
            ge="128",
            le="128",
            action="deny",
            command="",
        ),
        # REGRA DENY AS PREFIXO
        # RuleWithIPv6(
        #   condition="x.x.x.x/xx",
        #   ge="XX",
        #   le="128",
        #   action="deny",
        #   command="",
        # ),
        RuleWithIPv6(
            condition="::/0",
            ge="10",
            le="128",
            action="permit",
            command="display bgp ipv6 routing-table {target} | no-more",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

HuaweiBGPASPathTable = BuiltinDirective(
    id="__hyperglass_huawei_bgp_aspath_table__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'display bgp routing-table regular-expression "{target}"',
                'display bgp ipv6 routing-table regular-expression "{target}"',
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

HuaweiBGPCommunityTable = BuiltinDirective(
    id="__hyperglass_huawei_bgp_community_table__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                'display bgp routing-table community "{target}"',
                'display bgp ipv6 routing-table community "{target}"',
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)
