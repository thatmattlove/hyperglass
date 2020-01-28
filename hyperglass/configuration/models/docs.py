"""Configuration for API docs feature."""
# Third Party Imports
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import AnyUri
from hyperglass.configuration.models._utils import HyperglassModel


class Docs(HyperglassModel):
    """Validation model for params.docs."""

    enable: StrictBool = True
    mode: constr(regex=r"(swagger|redoc)") = "swagger"
    uri: AnyUri = "/docs"
    endpoint_summary: StrictStr = "Query Endpoint"
    endpoint_description: StrictStr = "Request a query response per-location."
    group_title: StrictStr = "Queries"
    openapi_url: AnyUri = "/openapi.json"
