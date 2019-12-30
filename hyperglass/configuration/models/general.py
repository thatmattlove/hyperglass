"""Validate general configuration variables."""

# Standard Library Imports
from typing import List

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class General(HyperglassModel):
    """Validation model for params.general."""

    debug: bool = False
    primary_asn: str = "65001"
    org_name: str = "The Company"
    google_analytics: str = ""
    redis_host: str = "localhost"
    redis_port: int = 6379
    requires_ipv6_cidr: List[str] = ["cisco_ios", "cisco_nxos"]
    request_timeout: int = 30
