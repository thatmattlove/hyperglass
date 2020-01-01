"""Validate feature configuration variables."""

# Standard Library Imports
from math import ceil

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

    class BgpCommunity(HyperglassModel):
        """Validation model for params.features.bgp_community."""

        enable: StrictBool = True

        class Regex(HyperglassModel):
            """Validation model for params.features.bgp_community.regex."""

            decimal: StrictStr = r"^[0-9]{1,10}$"
            extended_as: StrictStr = r"^([0-9]{0,5})\:([0-9]{1,5})$"
            large: StrictStr = r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"

        regex: Regex = Regex()

    class BgpAsPath(HyperglassModel):
        """Validation model for params.features.bgp_aspath."""

        enable: StrictBool = True

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

    class Traceroute(HyperglassModel):
        """Validation model for params.features.traceroute."""

        enable: StrictBool = True

    class Cache(HyperglassModel):
        """Validation model for params.features.cache."""

        redis_id: StrictInt = 0
        timeout: StrictInt = 120
        show_text: StrictBool = True
        text: StrictStr = "Results will be cached for {timeout} minutes.".format(
            timeout=ceil(timeout / 60)
        )

    class MaxPrefix(HyperglassModel):
        """Validation model for params.features.max_prefix."""

        enable: StrictBool = False
        ipv4: StrictInt = 24
        ipv6: StrictInt = 64
        message: StrictStr = (
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific."
        )

    class RateLimit(HyperglassModel):
        """Validation model for params.features.rate_limit."""

        redis_id: StrictInt = 1

        class Query(HyperglassModel):
            """Validation model for params.features.rate_limit.query."""

            rate: StrictInt = 5
            period: StrictStr = "minute"
            title: StrictStr = "Query Limit Reached"
            message: StrictStr = (
                "Query limit of {rate} per {period} reached. "
                "Please wait one minute and try again."
            ).format(rate=rate, period=period)
            button: StrictStr = "Try Again"

        class Site(HyperglassModel):
            """Validation model for params.features.rate_limit.site."""

            rate: StrictInt = 60
            period: StrictStr = "minute"
            title: StrictStr = "Limit Reached"
            subtitle: StrictStr = (
                "You have accessed this site more than {rate} "
                "times in the last {period}."
            ).format(rate=rate, period=period)
            button: StrictStr = "Try Again"

        query: Query = Query()
        site: Site = Site()

    bgp_route: BgpRoute = BgpRoute()
    bgp_community: BgpCommunity = BgpCommunity()
    bgp_aspath: BgpAsPath = BgpAsPath()
    ping: Ping = Ping()
    traceroute: Traceroute = Traceroute()
    cache: Cache = Cache()
    max_prefix: MaxPrefix = MaxPrefix()
    rate_limit: RateLimit = RateLimit()
