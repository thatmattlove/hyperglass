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

__all__ = (
    "BGPRoutePluginArista",
    "BGPRoutePluginFrr",
    "BGPRoutePluginJuniper",
    "BGPRoutePluginHuawei",
    "BGPSTRRoutePluginHuawei",
    "MikrotikGarbageOutput",
    "BGPSTRRoutePluginMikrotik",
    "MikrotikTargetNormalizerInput",
    "RemoveCommand",
)
