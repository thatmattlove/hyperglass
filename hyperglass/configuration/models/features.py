"""Validate feature configuration variables."""

# Standard Library Imports
from math import ceil

# Third Party Imports
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Features(HyperglassModel):
    """Validation model for params.features."""

    class BgpRoute(HyperglassModel):
        """Validation model for params.features.bgp_route."""

        enable: bool = True

    class BgpCommunity(HyperglassModel):
        """Validation model for params.features.bgp_community."""

        enable: bool = True

        class Regex(HyperglassModel):
            """Validation model for params.features.bgp_community.regex."""

            decimal: str = r"^[0-9]{1,10}$"
            extended_as: str = r"^([0-9]{0,5})\:([0-9]{1,5})$"
            large: str = r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"

        regex: Regex = Regex()

    class BgpAsPath(HyperglassModel):
        """Validation model for params.features.bgp_aspath."""

        enable: bool = True

        class Regex(HyperglassModel):
            """Validation model for params.bgp_aspath.regex."""

            mode: constr(regex="asplain|asdot") = "asplain"
            asplain: str = r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"
            asdot: str = (
                r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"
            )

        regex: Regex = Regex()

    class Ping(HyperglassModel):
        """Validation model for params.features.ping."""

        enable: bool = True

    class Traceroute(HyperglassModel):
        """Validation model for params.features.traceroute."""

        enable: bool = True

    class Cache(HyperglassModel):
        """Validation model for params.features.cache."""

        redis_id: int = 0
        timeout: int = 120
        show_text: bool = True
        text: str = "Results will be cached for {timeout} minutes.".format(
            timeout=ceil(timeout / 60)
        )

    class MaxPrefix(HyperglassModel):
        """Validation model for params.features.max_prefix."""

        enable: bool = False
        ipv4: int = 24
        ipv6: int = 64
        message: str = (
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific."
        )

    class RateLimit(HyperglassModel):
        """Validation model for params.features.rate_limit."""

        redis_id: int = 1

        class Query(HyperglassModel):
            """Validation model for params.features.rate_limit.query."""

            rate: int = 5
            period: str = "minute"
            title: str = "Query Limit Reached"
            message: str = (
                "Query limit of {rate} per {period} reached. "
                "Please wait one minute and try again."
            ).format(rate=rate, period=period)
            button: str = "Try Again"

        class Site(HyperglassModel):
            """Validation model for params.features.rate_limit.site."""

            rate: int = 60
            period: str = "minute"
            title: str = "Limit Reached"
            subtitle: str = (
                "You have accessed this site more than {rate} "
                "times in the last {period}."
            ).format(rate=rate, period=period)
            button: str = "Try Again"

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
