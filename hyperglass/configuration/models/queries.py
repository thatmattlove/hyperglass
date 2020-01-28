"""Validate query configuration parameters."""

# Third Party Imports
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.constants import SUPPORTED_QUERY_TYPES


class BgpCommunity(HyperglassModel):
    """Validation model for bgp_community configuration."""

    class Pattern(HyperglassModel):
        """Validation model for bgp_community regex patterns."""

        decimal: StrictStr = r"^[0-9]{1,10}$"
        extended_as: StrictStr = r"^([0-9]{0,5})\:([0-9]{1,5})$"
        large: StrictStr = r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"

    enable: StrictBool = True
    display_name: StrictStr = "BGP Community"
    pattern: Pattern = Pattern()


class BgpRoute(HyperglassModel):
    """Validation model for bgp_route configuration."""

    enable: StrictBool = True
    display_name: StrictStr = "BGP Route"


class BgpAsPath(HyperglassModel):
    """Validation model for bgp_aspath configuration."""

    enable: StrictBool = True
    display_name: StrictStr = "BGP AS Path"

    class Pattern(HyperglassModel):
        """Validation model for bgp_aspath regex patterns."""

        mode: constr(regex="asplain|asdot") = "asplain"
        asplain: StrictStr = r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"
        asdot: StrictStr = (
            r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"
        )

    pattern: Pattern = Pattern()


class Ping(HyperglassModel):
    """Validation model for ping configuration."""

    enable: StrictBool = True
    display_name: StrictStr = "Ping"


class Traceroute(HyperglassModel):
    """Validation model for traceroute configuration."""

    enable: StrictBool = True
    display_name: StrictStr = "Traceroute"


class Queries(HyperglassModel):
    """Validation model for all query types."""

    class MaxPrefix(HyperglassModel):
        """Validation model for params.features.max_prefix."""

        enable: StrictBool = False
        ipv4: StrictInt = 24
        ipv6: StrictInt = 64
        message: StrictStr = (
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific."
        )

    @property
    def map(self):
        """Return a dict of all query display names, internal names, and enable state.

        Returns:
            {dict} -- Dict of queries.
        """
        _map = {}
        for query in SUPPORTED_QUERY_TYPES:
            query_obj = getattr(self, query)
            _map[query] = {
                "name": query,
                "display_name": query_obj.display_name,
                "enable": query_obj.enable,
            }
        return _map

    @property
    def list(self):
        """Return a list of all query display names, internal names, and enable state.

        Returns:
            {list} -- Dict of queries.
        """
        _list = []
        for query in SUPPORTED_QUERY_TYPES:
            query_obj = getattr(self, query)
            _list.append(
                {
                    "name": query,
                    "display_name": query_obj.display_name,
                    "enable": query_obj.enable,
                }
            )
        return _list

    bgp_route: BgpRoute = BgpRoute()
    bgp_community: BgpCommunity = BgpCommunity()
    bgp_aspath: BgpAsPath = BgpAsPath()
    ping: Ping = Ping()
    traceroute: Traceroute = Traceroute()
    max_prefix: MaxPrefix = MaxPrefix()
