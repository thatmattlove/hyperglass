"""Configuration validation entry point."""

# Standard Library
from typing import List, Union, Optional
from ipaddress import ip_address

# Third Party
from pydantic import (
    Field,
    StrictInt,
    StrictStr,
    StrictBool,
    IPvAnyAddress,
    constr,
    validator,
)

# Local
from .web import Web
from .docs import Docs
from ..main import HyperglassModel
from .cache import Cache
from ..fields import IntFloat
from .logging import Logging
from .queries import Queries
from .messages import Messages
from .structured import Structured

Localhost = constr(regex=r"localhost")


class Params(HyperglassModel):
    """Validation model for all configuration variables."""

    # Top Level Params
    debug: StrictBool = Field(
        False,
        title="Debug",
        description="Enable debug mode. Warning: this will generate a *lot* of log output.",
    )
    developer_mode: StrictBool = Field(
        False,
        title="Developer Mode",
        description='Enable developer mode. If enabled, the hyperglass backend (Python) and frontend (React/Javascript) applications are "unlinked", so that React tools can be used for front end development. A `<Debugger />` convenience component is also displayed in the UI for easier UI development.',
    )
    primary_asn: Union[StrictInt, StrictStr] = Field(
        "65001",
        title="Primary ASN",
        description="Your network's primary ASN. This field is used to set some useful defaults such as the subtitle and PeeringDB URL.",
    )
    org_name: StrictStr = Field(
        "Beloved Hyperglass User",
        title="Organization Name",
        description="Your organization's name. This field is used in the UI & API documentation to set fields such as `<meta/>` HTML tags for SEO and the terms & conditions footer component.",
    )
    site_title: StrictStr = Field(
        "hyperglass",
        title="Site Title",
        description="The name of your hyperglass site. This field is used in the UI & API documentation to set fields such as the `<title/>` HTML tag, and the terms & conditions footer component.",
    )
    site_description: StrictStr = Field(
        "{org_name} Network Looking Glass",
        title="Site Description",
        description='A short description of your hyperglass site. This field is used in th UI & API documentation to set the `<meta name="description"/>` tag. `{org_name}` may be used to insert the value of the `org_name` field.',
    )
    site_keywords: List[StrictStr] = Field(
        [
            "hyperglass",
            "looking glass",
            "lg",
            "peer",
            "peering",
            "ip",
            "ipv4",
            "ipv6",
            "transit",
            "community",
            "communities",
            "bgp",
            "routing",
            "network",
            "isp",
            "internet service provider",
        ],
        title="Site Keywords",
        description='Keywords pertaining to your hyperglass site. This field is used to generate `<meta name="keywords"/>` HTML tags, which helps tremendously with SEO.',
    )
    request_timeout: StrictInt = Field(
        90,
        title="Request Timeout",
        description="Global timeout in seconds for all requests. The frontend application (UI) uses this field's exact value when submitting queries. The backend application uses this field's value, minus one second, for its own timeout handling. This is to ensure a contextual timeout error is presented to the end user in the event of a backend application timeout.",
    )
    listen_address: Optional[Union[IPvAnyAddress, Localhost]] = Field(
        None,
        title="Listen Address",
        description="Local IP Address or hostname the hyperglass application listens on to serve web traffic.",
    )
    listen_port: StrictInt = Field(
        8001,
        title="Listen Port",
        description="Local TCP port the hyperglass application listens on to serve web traffic.",
    )
    cors_origins: List[StrictStr] = Field(
        [],
        title="Cross-Origin Resource Sharing",
        description="Allowed CORS hosts. By default, no CORS hosts are allowed.",
    )
    netmiko_delay_factor: IntFloat = Field(
        0.1,
        title="Netmiko Delay Factor",
        description="Override the netmiko global delay factor.",
    )

    # Sub Level Params
    cache: Cache = Cache()
    docs: Docs = Docs()
    logging: Logging = Logging()
    messages: Messages = Messages()
    queries: Queries = Queries()
    structured: Structured = Structured()
    web: Web = Web()

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 1}

    @validator("listen_address", pre=True, always=True)
    def validate_listen_address(cls, value, values):
        """Set default listen_address based on debug mode.

        Arguments:
            value {str|IPvAnyAddress|None} -- listen_address
            values {dict} -- already-validated entries before listen_address

        Returns:
            {str} -- Validated listen_address
        """
        if value is None and not values["debug"]:
            listen_address = ip_address("127.0.0.1")
        elif value is None and values["debug"]:
            listen_address = ip_address("0.0.0.0")  # noqa: S104
        elif isinstance(value, str) and value != "localhost":
            try:
                listen_address = ip_address(value)
            except ValueError:
                raise ValueError(str(value))
        elif isinstance(value, str) and value == "localhost":
            listen_address = ip_address("127.0.0.1")
        else:
            raise ValueError(str(value))
        return listen_address

    @validator("site_description")
    def validate_site_description(cls, value, values):
        """Format the site descripion with the org_name field.

        Arguments:
            value {str} -- site_description
            values {str} -- Values before site_description

        Returns:
            {str} -- Formatted description
        """
        return value.format(org_name=values["org_name"])

    @validator("primary_asn")
    def validate_primary_asn(cls, value):
        """Stringify primary_asn if passed as an integer.

        Arguments:
            value {str|int} -- Unvalidated Primary ASN

        Returns:
            {str} -- Stringified Primary ASN.
        """
        if not isinstance(value, str):
            value = str(value)
        return value
