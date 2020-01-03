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


class General(HyperglassModel):
    """Validation model for params.general."""

    debug: StrictBool = False
    primary_asn: StrictStr = "65001"
    org_name: StrictStr = "The Company"
    google_analytics: StrictStr = ""
    redis_host: StrictStr = "localhost"
    redis_port: StrictInt = 6379
    requires_ipv6_cidr: List[StrictStr] = ["cisco_ios", "cisco_nxos"]
    request_timeout: StrictInt = 30
    listen_address: Union[IPvAnyAddress, StrictStr] = "localhost"
    listen_port: StrictInt = 8001
    log_file: Optional[FilePath]

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
