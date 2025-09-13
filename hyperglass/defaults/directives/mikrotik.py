"""Default Mikrotik Directives."""

# Project
from hyperglass.models.directive import (
    Text,
    RuleWithIPv4,
    RuleWithIPv6,
    RuleWithPattern,
    BuiltinDirective,
)

__all__ = (
    "Mikrotik_BGPASPath",
    "Mikrotik_BGPCommunity",
    "Mikrotik_BGPRoute",
    "Mikrotik_Ping",
    "Mikrotik_Traceroute",
    "MikrotikBGPRouteTable",
    "MikrotikBGPASPathTable",
    "MikrotikBGPCommunityTable",
)

NAME = "Mikrotik"
PLATFORMS = ["mikrotik_routeros", "mikrotik_switchos"]

Mikrotik_BGPRoute = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_route__",
    name="BGP Route",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            ge="8",
            le="32",
            action="permit",
            command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=0.0.0.0/0",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=::/0",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    plugins=["mikrotik_normalize_input", "mikrotik_garbage_output", "bgp_routestr_mikrotik"],
    table_output="__hyperglass_mikrotik_bgp_route_table__",
    platforms=PLATFORMS,
)

Mikrotik_BGPASPath = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "ip route print where bgp-as-path={target}",
                "ipv6 route print where bgp-as-path={target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    plugins=["mikrotik_normalize_input","mikrotik_garbage_output", "bgp_routestr_mikrotik"],
    table_output="__hyperglass_mikrotik_bgp_aspath_table__",
    platforms=PLATFORMS,
)

Mikrotik_BGPCommunity = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_community__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "ip route print where bgp-communities={target}",
                "ipv6 route print where bgp-communities={target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    plugins=["mikrotik_normalize_input","mikrotik_garbage_output", "bgp_routestr_mikrotik"],
    table_output="__hyperglass_mikrotik_bgp_community_table__",
    platforms=PLATFORMS,
)

Mikrotik_Ping = BuiltinDirective(
    id="__hyperglass_mikrotik_ping__",
    name="Ping",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="ping src-address={source4} count=5 {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="ping src-address={source6} count=5 {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

Mikrotik_Traceroute = BuiltinDirective(
    id="__hyperglass_mikrotik_traceroute__",
    name="Traceroute",
    rules=[
        RuleWithIPv4(
            condition="0.0.0.0/0",
            action="permit",
            command="tool traceroute src-address={source4} timeout=1 duration=5 count=1 {target}",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="tool traceroute src-address={source6} timeout=1 duration=5 count=1 {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

# Table Output Directives

MikrotikBGPRouteTable = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_route_table__",
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
        # Regra DENY RFC 1918 classe A
        RuleWithIPv4(
            condition="10.0.0.0/8",
            ge="8",
            le="32",
            action="deny",
            command="",
        ),
        # Regra DENY RFC 1918 classe B
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
        # Regra DENY ASN PREFIXO
        RuleWithIPv4(
            condition="${ASN-IPv4}",
            ge="${mask}",
            le="32",
            action="deny",
            command="",
        ),
        RuleWithIPv4(
            condition="0.0.0.0/0",
            ge="8",
            le="32",
            action="permit",
            command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=0.0.0.0/0",
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
        # REGRA DENY ASN PREFIXO
        RuleWithIPv6(
            condition="${ASN-IPv6}",
            ge="${mask}",
            le="128",
            action="deny",
            command="",
        ),
        RuleWithIPv6(
            condition="::/0",
            action="permit",
            command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=::/0",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=PLATFORMS,
)

MikrotikBGPASPathTable = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_aspath_table__",
    name="BGP AS Path",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "routing route print detail without-paging where bgp-as-path~{target}",
                "routing route print detail without-paging where bgp-as-path~{target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=PLATFORMS,
)

MikrotikBGPCommunityTable = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_community_table__",
    name="BGP Community",
    rules=[
        RuleWithPattern(
            condition="*",
            action="permit",
            commands=[
                "routing route print detail without-paging where bgp-communities~{target}",
                "routing route print detail without-paging where bgp-communities~{target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=PLATFORMS,
)
