"""Validate general configuration variables."""

# Standard Library Imports
from datetime import datetime
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
from hyperglass.configuration.models.opengraph import OpenGraph


class General(HyperglassModel):
    """Validation model for params.general."""

    debug: StrictBool = False
    primary_asn: StrictStr = "65001"
    org_name: StrictStr = "The Company"
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
    opengraph: OpenGraph = OpenGraph()
    google_analytics: StrictStr = ""
    redis_host: StrictStr = "localhost"
    redis_port: StrictInt = 6379
    requires_ipv6_cidr: List[StrictStr] = ["cisco_ios", "cisco_nxos"]
    request_timeout: StrictInt = 30
    listen_address: Union[IPvAnyAddress, StrictStr] = "localhost"
    listen_port: StrictInt = 8001
    log_file: Optional[FilePath]

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
