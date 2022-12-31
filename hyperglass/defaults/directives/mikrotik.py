"""Default Mikrotik Directives."""

# Project
from hyperglass.models.directive import Rule, Text, BuiltinDirective

__all__ = (
    "Mikrotik_BGPASPath",
    "Mikrotik_BGPCommunity",
    "Mikrotik_BGPRoute",
    "Mikrotik_Ping",
    "Mikrotik_Traceroute",
)

Mikrotik_BGPRoute = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_route__",
    name="BGP Route",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ip route print where dst-address={target}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ipv6 route print where dst-address={target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["mikrotik_routeros", "mikrotik_switchos"],
)

Mikrotik_BGPASPath = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_aspath__",
    name="BGP AS Path",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "ip route print where bgp-as-path={target}",
                "ipv6 route print where bgp-as-path={target}",
            ],
        )
    ],
    field=Text(description="AS Path Regular Expression"),
    platforms=["mikrotik_routeros", "mikrotik_switchos"],
)

Mikrotik_BGPCommunity = BuiltinDirective(
    id="__hyperglass_mikrotik_bgp_community__",
    name="BGP Community",
    rules=[
        Rule(
            condition="*",
            action="permit",
            commands=[
                "ip route print where bgp-communities={target}",
                "ipv6 route print where bgp-communities={target}",
            ],
        )
    ],
    field=Text(description="BGP Community String"),
    platforms=["mikrotik_routeros", "mikrotik_switchos"],
)

Mikrotik_Ping = BuiltinDirective(
    id="__hyperglass_mikrotik_ping__",
    name="Ping",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="ping src-address={source4} count=5 {target}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="ping src-address={source6} count=5 {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["mikrotik_routeros", "mikrotik_switchos"],
)

Mikrotik_Traceroute = BuiltinDirective(
    id="__hyperglass_mikrotik_traceroute__",
    name="Traceroute",
    rules=[
        Rule(
            condition="0.0.0.0/0",
            action="permit",
            command="tool traceroute src-address={source4} timeout=1 duration=5 count=1 {target}",
        ),
        Rule(
            condition="::/0",
            action="permit",
            command="tool traceroute src-address={source6} timeout=1 duration=5 count=1 {target}",
        ),
    ],
    field=Text(description="IP Address, Prefix, or Hostname"),
    platforms=["mikrotik_routeros", "mikrotik_switchos"],
)