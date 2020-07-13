"""Structured data configuration variables."""

# Standard Library
from typing import List

# Third Party
from pydantic import StrictStr, constr

# Project
from hyperglass.models import HyperglassModel

StructuredCommunityMode = constr(regex=r"(permit|deny)")
StructuredRPKIMode = constr(regex=r"(router|external)")


class StructuredCommunities(HyperglassModel):
    """Control structured data response for BGP communties."""

    mode: StructuredCommunityMode = "deny"
    items: List[StrictStr] = []


class StructuredRpki(HyperglassModel):
    """Control structured data response for RPKI state."""

    mode: StructuredRPKIMode = "router"


class Structured(HyperglassModel):
    """Control structured data responses."""

    communities: StructuredCommunities = StructuredCommunities()
    rpki: StructuredRpki = StructuredRpki()
