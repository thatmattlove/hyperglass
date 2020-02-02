"""Validate SSL configuration variables."""

# Standard Library Imports
from typing import Optional

# Third Party Imports
from pydantic import Field
from pydantic import FilePath
from pydantic import StrictBool

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


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
