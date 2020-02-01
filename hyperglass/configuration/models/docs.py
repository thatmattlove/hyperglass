"""Configuration for API docs feature."""
# Third Party Imports
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import AnyUri
from hyperglass.configuration.models._utils import HyperglassModel


class EndpointConfig(HyperglassModel):
    """Validation model for per API endpoint documentation."""

    title: StrictStr
    description: StrictStr
    summary: StrictStr


class Docs(HyperglassModel):
    """Validation model for params.docs."""

    enable: StrictBool = True
    mode: constr(regex=r"(swagger|redoc)") = "swagger"
    uri: AnyUri = "/docs"
    openapi_url: AnyUri = "/openapi.json"
    query: EndpointConfig = {
        "title": "Submit Query",
        "description": "Request a query response per-location.",
        "summary": "Query the Looking Glass",
    }
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
