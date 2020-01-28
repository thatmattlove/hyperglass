"""Validate feature configuration variables."""

# Third Party Imports
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Features(HyperglassModel):
    """Validation model for params.features."""

    class BgpRoute(HyperglassModel):
        """Validation model for params.features.bgp_route."""

        enable: StrictBool = True
        display_name: StrictStr = "BGP Route"

    class BgpCommunity(HyperglassModel):
        """Validation model for params.features.bgp_community."""

        enable: StrictBool = True
        display_name: StrictStr = "BGP Community"

        class Regex(HyperglassModel):
            """Validation model for params.features.bgp_community.regex."""

            decimal: StrictStr = r"^[0-9]{1,10}$"
            extended_as: StrictStr = r"^([0-9]{0,5})\:([0-9]{1,5})$"
            large: StrictStr = r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"

        regex: Regex = Regex()

    class BgpAsPath(HyperglassModel):
        """Validation model for params.features.bgp_aspath."""

        enable: StrictBool = True
        display_name: StrictStr = "BGP AS Path"

        class Regex(HyperglassModel):
            """Validation model for params.bgp_aspath.regex."""

            mode: constr(regex="asplain|asdot") = "asplain"
            asplain: StrictStr = r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"
            asdot: StrictStr = (
                r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"
            )

        regex: Regex = Regex()

    class Ping(HyperglassModel):
        """Validation model for params.features.ping."""

        enable: StrictBool = True
        display_name: StrictStr = "Ping"

    class Traceroute(HyperglassModel):
        """Validation model for params.features.traceroute."""

        enable: StrictBool = True
        display_name: StrictStr = "Traceroute"

    class MaxPrefix(HyperglassModel):
        """Validation model for params.features.max_prefix."""

        enable: StrictBool = False
        ipv4: StrictInt = 24
        ipv6: StrictInt = 64
        message: StrictStr = (
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific."
        )

    bgp_route: BgpRoute = BgpRoute()
    bgp_community: BgpCommunity = BgpCommunity()
    bgp_aspath: BgpAsPath = BgpAsPath()
    ping: Ping = Ping()
    traceroute: Traceroute = Traceroute()
    max_prefix: MaxPrefix = MaxPrefix()
