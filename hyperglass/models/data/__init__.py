"""Data structure models."""

# Standard Library
from typing import Union

# Local
from .bgp_route import BGPRouteTable

OutputDataModel = Union[BGPRouteTable]

__all__ = (
    "BGPRouteTable",
    "OutputDataModel",
)
