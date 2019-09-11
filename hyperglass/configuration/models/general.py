"""
Defines models for General config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List
from typing import Union

# Third Party Imports
from pydantic import BaseSettings
from pydantic import IPvAnyNetwork


class General(BaseSettings):
    """Class model for params.general"""

    debug: bool = False
    primary_asn: str = "65001"
    org_name: str = "The Company"
    google_analytics: Union[str, None] = None
    redis_host: Union[str, IPvAnyNetwork] = "localhost"
    redis_port: int = 6379
    requires_ipv6_cidr: List[str] = ["cisco_ios", "cisco_nxos"]
    request_timeout: int = 15
