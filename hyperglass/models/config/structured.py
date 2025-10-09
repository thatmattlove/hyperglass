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
    """Control IP enrichment for structured data responses using real-time BGP.TOOLS lookups."""

    enrich_traceroute: bool = True
    """Enable ASN/org/IP enrichment for traceroute hops using real-time BGP.TOOLS data."""

    @field_validator("enrich_traceroute")
    def validate_enrich_traceroute(cls, value: bool) -> bool:
        """Validate traceroute enrichment setting."""
        return value


class Structured(HyperglassModel):
    """Control structured data responses."""

    communities: StructuredCommunities = StructuredCommunities()
    rpki: StructuredRpki = StructuredRpki()
    ip_enrichment: StructuredIpEnrichment = StructuredIpEnrichment()

    # Top-level structured enable/disable flags. If `structured:` is present in
    # the user's config and these are not set (None), the structured table
    # output is considered enabled by default. Setting them to False disables
    # the structured table output even when a `structured:` block exists.
    enable_for_traceroute: t.Optional[bool] = None
    enable_for_bgp_route: t.Optional[bool] = None
