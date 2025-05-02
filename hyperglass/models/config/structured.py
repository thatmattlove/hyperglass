"""Structured data configuration variables."""

# Standard Library
import typing as t

# Local
from ..main import HyperglassModel

StructuredCommunityMode = t.Literal["permit", "deny"]
StructuredRPKIMode = t.Literal["router", "external"]


class StructuredCommunities(HyperglassModel):
    """Control structured data response for BGP communities."""

    mode: StructuredCommunityMode = "deny"
    items: t.List[str] = []


class StructuredRpki(HyperglassModel):
    """Control structured data response for RPKI state."""

    mode: StructuredRPKIMode = "router"


class Structured(HyperglassModel):
    """Control structured data responses."""

    communities: StructuredCommunities = StructuredCommunities()
    rpki: StructuredRpki = StructuredRpki()
