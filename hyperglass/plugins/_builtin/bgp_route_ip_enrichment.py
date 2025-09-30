"""IP enrichment for structured BGP route data - show path functionality."""

# Standard Library
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.plugins._output import OutputPlugin
from hyperglass.models.data.bgp_route import BGPRouteTable

if t.TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query


class ZBgpRouteIpEnrichment(OutputPlugin):

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = (
        "mikrotik_routeros",
        "mikrotik_switchos",
        "mikrotik",
        "cisco_ios",
        "juniper_junos",
        "arista_eos",
        "frr",
        "huawei",
        "huawei_vrpv8",
    )
    directives: t.Sequence[str] = ("bgp_route", "bgp_community")
    common: bool = True

    def process(self, *, output: "OutputDataModel", query: "Query") -> "OutputDataModel":

        if not isinstance(output, BGPRouteTable):
            return output

        _log = log.bind(plugin=self.__class__.__name__)

        return output
