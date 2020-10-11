"""Validate SSL configuration variables."""

# Standard Library
from typing import Optional

# Third Party
from pydantic import Field, FilePath, StrictBool

# Local
from ..main import HyperglassModel


class Ssl(HyperglassModel):
    """Validate SSL config parameters."""

    enable: StrictBool = Field(
        True,
        title="Enable SSL",
        description="If enabled, hyperglass will use HTTPS to connect to the configured device running [hyperglass-agent](/fixme). If enabled, a certificate file must be specified (hyperglass does not support connecting to a device over an unverified SSL session.)",
    )
    cert: Optional[FilePath]

    class Config:
        """Pydantic model configuration."""

        title = "SSL"
        description = "SSL configuration for devices running hyperglass-agent."
        fields = {
            "cert": {
                "title": "Certificate",
                "description": "Valid path to an SSL certificate. This certificate must be the public key used to serve the hyperglass-agent API on the device running hyperglass-agent.",
            }
        }
