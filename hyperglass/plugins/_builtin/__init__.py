"""Built-in hyperglass plugins."""

# Local
from .remove_command import RemoveCommand
from .bgp_route_arista import BGPRoutePluginArista
from .bgp_route_frr import BGPRoutePluginFrr
from .bgp_route_juniper import BGPRoutePluginJuniper
from .mikrotik_garbage_output import MikrotikGarbageOutput

__all__ = (
    "BGPRoutePluginArista",
    "BGPRoutePluginFrr",
    "BGPRoutePluginJuniper",
    "MikrotikGarbageOutput",
    "RemoveCommand",
)
