"""Configuration for API docs feature."""
# Third Party Imports
from pydantic import Field
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import AnyUri
from hyperglass.configuration.models._utils import HyperglassModel


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
    mode: constr(regex=r"(swagger|redoc)") = Field(
        "swagger",
        title="Docs Mode",
        description="OpenAPI UI library to use for the hyperglass API docs. Currently, the options are [Swagger UI](/fixme) and [Redoc](/fixme).",
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
        }
