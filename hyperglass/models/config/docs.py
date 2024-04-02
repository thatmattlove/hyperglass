"""Configuration for API docs feature."""

# Standard Library
import typing as t

# Third Party
from pydantic import Field, HttpUrl

# Local
from ..main import HyperglassModel
from ..fields import AnyUri

DocsMode = t.Literal["swagger", "redoc"]


class EndpointConfig(HyperglassModel):
    """Validation model for per API endpoint documentation."""

    title: str = Field(
        ...,
        title="Endpoint Title",
        description="Displayed as the header text above the API endpoint section.",
    )
    description: str = Field(
        ...,
        title="Endpoint Description",
        description="Displayed inside each API endpoint section.",
    )
    summary: str = Field(
        ...,
        title="Endpoint Summary",
        description="Displayed beside the API endpoint URI.",
    )


class Docs(HyperglassModel):
    """Validation model for params.docs."""

    enable: bool = Field(True, title="Enable", description="Enable or disable API documentation.")
    base_url: HttpUrl = Field(
        "https://lg.example.net",
        title="Base URL",
        description="Base URL used in request samples.",
    )
    path: AnyUri = Field(
        "/api/docs",
        title="URI",
        description="HTTP URI/path where API documentation can be accessed.",
    )
    title: str = Field(
        "{site_title} API Documentation",
        title="Title",
        description="API documentation title. `{site_title}` may be used to display the `site_title` parameter.",
    )
    description: str = Field(
        "",
        title="Description",
        description="API documentation description appearing below the title.",
    )
    query: EndpointConfig = EndpointConfig(
        title="Submit Query",
        description="Request a query response per-location.",
        summary="Query the Looking Glass",
    )
    devices: EndpointConfig = EndpointConfig(
        title="Devices",
        description="List of all devices/locations with associated identifiers, display names, networks, & VRFs.",
        summary="Devices List",
    )
    queries: EndpointConfig = EndpointConfig(
        title="Supported Queries",
        description="List of supported query types.",
        summary="Query Types",
    )
    info: EndpointConfig = EndpointConfig(
        title="System Information",
        description="General information about this looking glass.",
        summary="System Information",
    )
