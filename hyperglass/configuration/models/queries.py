"""Validate query configuration parameters."""

# Third Party
from pydantic import Field, StrictStr, StrictBool, constr

# Project
from hyperglass.constants import SUPPORTED_QUERY_TYPES
from hyperglass.configuration.models._utils import HyperglassModel


class HyperglassLevel3(HyperglassModel):
    """Automatic docs sorting subclass."""

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 3}


class HyperglassLevel4(HyperglassModel):
    """Automatic docs sorting subclass."""

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 4}


class BgpCommunityPattern(HyperglassLevel4):
    """Validation model for bgp_community regex patterns."""

    decimal: StrictStr = Field(
        r"^[0-9]{1,10}$",
        title="Decimal Community",
        description="Regular expression pattern for validating decimal type BGP Community strings.",
    )
    extended_as: StrictStr = Field(
        r"^([0-9]{0,5})\:([0-9]{1,5})$",
        title="Extended AS Community",
        description="Regular expression pattern for validating extended AS type BGP Community strings, e.g. `65000:1`",
    )
    large: StrictStr = Field(
        r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$",
        title="Large Community",
        description="Regular expression pattern for validating large community strings, e.g. `65000:65001:65002`",
    )

    class Config:
        """Pydantic model configuration."""

        title = "Pattern"
        description = (
            "Regular expression patterns used to validate BGP Community queries."
        )


class BgpAsPathPattern(HyperglassLevel4):
    """Validation model for bgp_aspath regex patterns."""

    mode: constr(regex=r"asplain|asdot") = Field(
        "asplain",
        title="AS Path Mode",
        description="Set ASN display mode. This field is dependent on how your network devices are configured.",
    )
    asplain: StrictStr = Field(
        r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$",
        title="AS Plain",
        description="Regular expression pattern for validating [AS Plain](/fixme) type BGP AS Path queries.",
    )
    asdot: StrictStr = Field(
        r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$",
        title="AS Dot",
        description="Regular expression pattern for validating [AS Dot](/fixme) type BGP AS Path queries.",
    )

    class Config:
        """Pydantic model configuration."""

        title = "Pattern"
        description = (
            "Regular expression patterns used to validate BGP AS Path queries."
        )


class BgpCommunity(HyperglassLevel3):
    """Validation model for bgp_community configuration."""

    enable: StrictBool = Field(
        True,
        title="Enable",
        description="Enable or disable the BGP Community query type.",
    )
    display_name: StrictStr = Field(
        "BGP Community",
        title="Display Name",
        description="Text displayed for the BGP Community query type in the hyperglas UI.",
    )
    pattern: BgpCommunityPattern = BgpCommunityPattern()


class BgpRoute(HyperglassLevel3):
    """Validation model for bgp_route configuration."""

    enable: StrictBool = Field(
        True, title="Enable", description="Enable or disable the BGP Route query type."
    )
    display_name: StrictStr = Field(
        "BGP Route",
        title="Display Name",
        description="Text displayed for the BGP Route query type in the hyperglas UI.",
    )


class BgpAsPath(HyperglassLevel3):
    """Validation model for bgp_aspath configuration."""

    enable: StrictBool = Field(
        True,
        title="Enable",
        description="Enable or disable the BGP AS Path query type.",
    )
    display_name: StrictStr = Field(
        "BGP AS Path",
        title="Display Name",
        description="Text displayed for the BGP AS Path query type in the hyperglas UI.",
    )
    pattern: BgpAsPathPattern = BgpAsPathPattern()


class Ping(HyperglassLevel3):
    """Validation model for ping configuration."""

    enable: StrictBool = Field(
        True, title="Enable", description="Enable or disable the Ping query type."
    )
    display_name: StrictStr = Field(
        "Ping",
        title="Display Name",
        description="Text displayed for the Ping query type in the hyperglas UI.",
    )


class Traceroute(HyperglassLevel3):
    """Validation model for traceroute configuration."""

    enable: StrictBool = Field(
        True, title="Enable", description="Enable or disable the Traceroute query type."
    )
    display_name: StrictStr = Field(
        "Traceroute",
        title="Display Name",
        description="Text displayed for the Traceroute query type in the hyperglas UI.",
    )


class Queries(HyperglassModel):
    """Validation model for all query types."""

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

    class Config:
        """Pydantic model configuration."""

        title = "Queries"
        description = "Enable, disable, or configure query types."
        fields = {
            "bgp_route": {
                "title": "BGP Route",
                "description": "Enable, disable, or configure the BGP Route query type.",
            },
            "bgp_community": {
                "title": "BGP Community",
                "description": "Enable, disable, or configure the BGP Community query type.",
            },
            "bgp_aspath": {
                "title": "BGP AS Path",
                "description": "Enable, disable, or configure the BGP AS Path query type.",
            },
            "ping": {
                "title": "Ping",
                "description": "Enable, disable, or configure the Ping query type.",
            },
            "traceroute": {
                "title": "Traceroute",
                "description": "Enable, disable, or configure the Traceroute query type.",
            },
        }
        schema_extra = {"level": 2}
