"""Configuration for API docs feature."""
# Third Party
from pydantic import Field, HttpUrl, StrictStr, StrictBool, constr

# Project
from hyperglass.models import HyperglassModel
from hyperglass.models.fields import AnyUri

DocsMode = constr(regex=r"(swagger|redoc)")


class EndpointConfig(HyperglassModel):
    """Validation model for per API endpoint documentation."""

    title: StrictStr = Field(
        ...,
        title="Endpoint Title",
        description="Displayed as the header text above the API endpoint section.",
    )
    description: StrictStr = Field(
        ...,
        title="Endpoint Description",
        description="Displayed inside each API endpoint section.",
    )
    summary: StrictStr = Field(
        ...,
        title="Endpoint Summary",
        description="Displayed beside the API endpoint URI.",
    )


class Docs(HyperglassModel):
    """Validation model for params.docs."""

    enable: StrictBool = Field(
        True, title="Enable", description="Enable or disable API documentation."
    )
    mode: DocsMode = Field(
        "redoc",
        title="Docs Mode",
        description="OpenAPI UI library to use for the hyperglass API docs. Currently, the options are [Swagger UI](/fixme) and [Redoc](/fixme).",
    )
    base_url: HttpUrl = Field(
        "https://lg.example.net",
        title="Base URL",
        description="Base URL used in request samples.",
    )
    uri: AnyUri = Field(
        "/api/docs",
        title="URI",
        description="HTTP URI/path where API documentation can be accessed.",
    )
    openapi_uri: AnyUri = Field(
        "/openapi.json",
        title="OpenAPI URI",
        description="Path to the automatically generated `openapi.json` file.",
    )
    title: StrictStr = Field(
        "{site_title} API Documentation",
        title="Title",
        description="API documentation title. `{site_title}` may be used to display the `site_title` parameter.",
    )
    description: StrictStr = Field(
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
    communities: EndpointConfig = EndpointConfig(
        title="BGP Communities",
        description="List of BGP communities.",
        summary="BGP Communities List",
    )
    info: EndpointConfig = EndpointConfig(
        title="System Information",
        description="General information about this looking glass.",
        summary="System Information",
    )

    class Config:
        """Pydantic model configuration."""

        title = "API Docs"
        description = "API documentation configuration parameters"
        fields = {
            "query": {
                "title": "Query API Endpoint",
                "description": "`/api/query/` API documentation options.",
            },
            "devices": {
                "title": "Devices API Endpoint",
                "description": "`/api/devices` API documentation options.",
            },
            "queries": {
                "title": "Queries API Endpoint",
                "description": "`/api/devices` API documentation options.",
            },
            "communities": {
                "title": "BGP Communities API Endpoint",
                "description": "`/api/communities` API documentation options.",
            },
        }
