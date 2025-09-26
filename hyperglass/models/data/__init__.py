"""Data structure models."""

# Standard Library
from typing import Union

# Local
from .bgp_route import BGPRoute, BGPRouteTable

OutputDataModel = Union[BGPRouteTable]

__all__ = (
    "BGPRoute",
    "BGPRouteTable",
    "OutputDataModel",
)
