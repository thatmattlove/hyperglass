"""Configuration validation entry point."""

# Standard Library Imports
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

# Third Party Imports
from pydantic import FilePath
from pydantic import IPvAnyAddress
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models.cache import Cache
from hyperglass.configuration.models.docs import Docs
from hyperglass.configuration.models.messages import Messages
from hyperglass.configuration.models.queries import Queries
from hyperglass.configuration.models.web import Web


class Params(HyperglassModel):
    """Validation model for all configuration variables."""

    # Top Level Params
    debug: StrictBool = False
    developer_mode: StrictBool = False
    primary_asn: Union[StrictInt, StrictStr] = "65001"
    org_name: StrictStr = "Beloved Hyperglass User"
    site_title: StrictStr = "hyperglass"
    site_description: StrictStr = "{org_name} Network Looking Glass"
    site_keywords: List[StrictStr] = [
        "hyperglass",
        "looking glass",
        "lg",
        "peer",
        "peering",
        "ipv4",
        "ipv6",
        "transit",
        "community",
        "communities",
        "bgp",
        "routing",
        "network",
        "isp",
    ]
    requires_ipv6_cidr: List[StrictStr] = ["cisco_ios", "cisco_nxos"]
    request_timeout: StrictInt = 30
    listen_address: Optional[Union[IPvAnyAddress, StrictStr]]
    listen_port: StrictInt = 8001
    log_file: Optional[FilePath]
    cors_origins: List[StrictStr] = []

    # Sub Level Params
    cache: Cache = Cache()
    docs: Docs = Docs()
    messages: Messages = Messages()
    queries: Queries = Queries()
    web: Web = Web()

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
            listen_address = "localhost"
        elif value is None and values["debug"]:
            listen_address = ip_address("0.0.0.0")  # noqa: S104
        elif isinstance(value, str) and value != "localhost":
            try:
                listen_address = ip_address(value)
            except ValueError:
                raise ValueError(str(value))
        elif isinstance(value, str) and value == "localhost":
            listen_address = value
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

    @validator("log_file")
    def validate_log_file(cls, value):
        """Set default logfile location if none is configured.

        Arguments:
            value {FilePath} -- Path to log file

        Returns:
            {Path} -- Logfile path object
        """
        if value is None:
            now = datetime.now()
            now.isoformat
            value = Path(
                f'/tmp/hyperglass_{now.strftime(r"%Y%M%d-%H%M%S")}.log'  # noqa: S108
            )
        return value

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
