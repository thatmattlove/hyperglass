"""Structured data configuration variables."""

# Standard Library
import typing as t

# Third Party
from pydantic import field_validator, ValidationInfo

# Local
from ..main import HyperglassModel

StructuredCommunityMode = t.Literal["permit", "deny", "name"]
StructuredRPKIMode = t.Literal["router", "external"]


class StructuredCommunities(HyperglassModel):
    """Control structured data response for BGP communities."""

    mode: StructuredCommunityMode = "deny"
    items: t.List[str] = []
    names: t.Dict[str, str] = {}

    @field_validator("names")
    def validate_names(cls, value: t.Dict[str, str], info: ValidationInfo) -> t.Dict[str, str]:
        """Validate that names are provided when mode is 'name'."""
        if info.data and info.data.get("mode") == "name" and not value:
            raise ValueError(
                "When using mode 'name', at least one community mapping must be provided in 'names'"
            )
        return value


class StructuredRpki(HyperglassModel):
    """Control structured data response for RPKI state."""

    mode: StructuredRPKIMode = "router"
    backend: str = "cloudflare"
    rpki_server_url: str = ""


class StructuredIpEnrichment(HyperglassModel):
    """Control IP enrichment for structured data responses."""

    enabled: bool = False
    cache_timeout: int = 86400  # 24 hours in seconds (minimum)
    enrich_next_hop: bool = False
    enrich_traceroute: bool = True

    @field_validator("cache_timeout")
    def validate_cache_timeout(cls, value: int) -> int:
        """Ensure cache timeout is at least 24 hours (86400 seconds)."""
        if value < 86400:
            return 86400
        return value


class Structured(HyperglassModel):
    """Control structured data responses."""

    communities: StructuredCommunities = StructuredCommunities()
    rpki: StructuredRpki = StructuredRpki()
    ip_enrichment: StructuredIpEnrichment = StructuredIpEnrichment()
