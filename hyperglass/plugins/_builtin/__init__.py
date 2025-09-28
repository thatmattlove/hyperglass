"""Built-in hyperglass plugins."""

# Local
from .bgp_route_frr import BGPRoutePluginFrr
from .remove_command import RemoveCommand
from .bgp_route_arista import BGPRoutePluginArista
from .bgp_route_huawei import BGPRoutePluginHuawei
from .bgp_routestr_huawei import BGPSTRRoutePluginHuawei
from .bgp_route_juniper import BGPRoutePluginJuniper
from .mikrotik_garbage_output import MikrotikGarbageOutput
from .bgp_routestr_mikrotik import BGPSTRRoutePluginMikrotik
from .mikrotik_normalize_input import MikrotikTargetNormalizerInput
from .traceroute_ip_enrichment import ZTracerouteIpEnrichment
from .bgp_route_ip_enrichment import ZBgpRouteIpEnrichment
from .trace_route_mikrotik import TraceroutePluginMikrotik
from .trace_route_huawei import TraceroutePluginHuawei

__all__ = (
    "BGPRoutePluginArista",
    "BGPRoutePluginFrr",
    "BGPRoutePluginJuniper",
    "BGPRoutePluginHuawei",
    "BGPSTRRoutePluginHuawei",
    "MikrotikGarbageOutput",
    "BGPSTRRoutePluginMikrotik",
    "MikrotikTargetNormalizerInput",
    "ZTracerouteIpEnrichment",
    "ZBgpRouteIpEnrichment",
    "TraceroutePluginMikrotik",
    "TraceroutePluginHuawei",
    "RemoveCommand",
)
