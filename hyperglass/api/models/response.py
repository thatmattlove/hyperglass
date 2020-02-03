"""Response model."""
# Standard Library
from typing import List

# Third Party
from pydantic import BaseModel, StrictStr, StrictBool, constr

# Project
from hyperglass.configuration import params


class QueryError(BaseModel):
    """Query response model."""

    output: StrictStr = params.messages.general
    level: constr(regex=r"(success|warning|error|danger)") = "danger"
    keywords: List[StrictStr] = []

    class Config:
        """Pydantic model configuration."""

        title = "Query Error"
        description = (
            "Response received when there is an error executing the requested query."
        )
        fields = {
            "output": {
                "title": "Output",
                "description": "Error Details",
                "example": "192.0.2.1/32 is not allowed.",
            },
            "level": {
                "title": "Level",
                "description": "Error Severity",
                "example": "danger",
            },
            "keywords": {
                "title": "Keywords",
                "description": "Relevant keyword values contained in the `output` field, which can be used for formatting.",
                "example": ["192.0.2.1/32"],
            },
        }
        schema_extra = {
            "examples": [
                {
                    "output": "192.0.2.1/32 is not allowed.",
                    "level": "danger",
                    "keywords": ["192.0.2.1/32"],
                }
            ]
        }


class QueryResponse(BaseModel):
    """Query response model."""

    output: StrictStr
    level: constr(regex=r"success") = "success"
    keywords: List[StrictStr] = []

    class Config:
        """Pydantic model configuration."""

        title = "Query Response"
        description = "Looking glass response"
        fields = {
            "level": {"title": "Level", "description": "Severity"},
            "keywords": {
                "title": "Keywords",
                "description": "Relevant keyword values contained in the `output` field, which can be used for formatting.",
                "example": ["1.1.1.0/24", "best #1"],
            },
            "output": {
                "title": "Output",
                "description": "Looking Glass Response",
                "example": """
BGP routing table entry for 1.1.1.0/24, version 224184946
BGP Bestpath: deterministic-med
Paths: (12 available, best #1, table default)
  Advertised to update-groups:
     1          40
  13335, (aggregated by 13335 172.68.129.1), (received & used)
    192.0.2.1 (metric 51) from 192.0.2.1 (192.0.2.1)
      Origin IGP, metric 0, localpref 250, valid, internal
      Community: 65000:1 65000:2
                """,
            },
        }
        schema_extra = {
            "examples": [
                {
                    "output": """
BGP routing table entry for 1.1.1.0/24, version 224184946
BGP Bestpath: deterministic-med
Paths: (12 available, best #1, table default)
  Advertised to update-groups:
     1          40
  13335, (aggregated by 13335 172.68.129.1), (received & used)
    192.0.2.1 (metric 51) from 192.0.2.1 (192.0.2.1)
      Origin IGP, metric 0, localpref 250, valid, internal
      Community: 65000:1 65000:2
                """,
                    "level": "success",
                    "keywords": ["1.1.1.0/24", "best #1"],
                }
            ]
        }


class Vrf(BaseModel):
    """Response model for /api/devices VRFs."""

    name: StrictStr
    display_name: StrictStr

    class Config:
        """Pydantic model configuration."""

        title = "VRF"
        description = "VRF attributes"
        schema_extra = {
            "examples": [
                {"name": "default", "display_name": "Global Routing Table"},
                {"name": "customer_vrf_name", "display_name": "Customer Name"},
            ]
        }


class Network(BaseModel):
    """Response model for /api/devices networks."""

    name: StrictStr
    display_name: StrictStr

    class Config:
        """Pydantic model configuration."""

        title = "Network"
        description = "Network/ASN attributes"
        schema_extra = {"examples": [{"name": "primary", "display_name": "AS65000"}]}


class RoutersResponse(BaseModel):
    """Response model for /api/devices list items."""

    name: StrictStr
    network: Network
    location: StrictStr
    display_name: StrictStr
    vrfs: List[Vrf]

    class Config:
        """Pydantic model configuration."""

        title = "Device"
        description = "Per-device attributes"
        schema_extra = {
            "examples": [
                {
                    "name": "router01-nyc01",
                    "location": "nyc01",
                    "display_name": "New York City, NY",
                }
            ]
        }


class SupportedQueryResponse(BaseModel):
    """Response model for /api/queries list items."""

    name: StrictStr
    display_name: StrictStr
    enable: StrictBool

    class Config:
        """Pydantic model configuration."""

        title = "Query Type"
        description = "If enabled is `true`, the `name` field may be used to specify the query type."
        schema_extra = {
            "examples": [
                {"name": "bgp_route", "display_name": "BGP Route", "enable": True}
            ]
        }
