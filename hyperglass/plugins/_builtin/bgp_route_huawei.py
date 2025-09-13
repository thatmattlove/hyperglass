# Standard Library
import typing as t
from ipaddress import ip_network

# Third Party
from pydantic import PrivateAttr

# Local
from .._input import InputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query

InputPluginTransformReturn = t.Union[t.Sequence[str], str]


class BGPRoutePluginHuawei(InputPlugin):
    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = (
        "huawei",
        "huawei_vrpv8",
    )
    directives: t.Sequence[str] = (
        "__hyperglass_huawei_bgp_route__",
        "__hyperglass_huawei_bgp_route_table__",
    )
    """
    Huawei BGP Route Input Plugin

    This plugin transforms a query target into a network address and prefix length
    ex.: 192.0.2.0/24 ->  192.0.2.0 24
    ex.: 2001:db8::/32 -> 2001:db8:: 32
    """

    def transform(self, query: "Query") -> InputPluginTransformReturn:
        target = query.query_target

        if not target:
            return None

        if isinstance(target, list):
            if len(target) == 0:
                return None
            target = target[0].strip()
        elif isinstance(target, str):
            target = target.strip()
        else:
            return None

        # Check for the / in the query target
        if target.find("/") == -1:
            return target

        try:
            target_network = ip_network(target)
            return f"{target_network.network_address!s} {target_network.prefixlen!s}"
        except ValueError:
            # Retorna o target original se for inválido
            return target
