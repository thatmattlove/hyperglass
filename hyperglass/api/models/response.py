"""Response model."""

# Standard Library
from typing import Dict, List, Union, Optional

# Third Party
from pydantic import BaseModel, StrictInt, StrictStr, StrictBool, constr

# Project
from hyperglass.configuration import params

ErrorName = constr(regex=r"(success|warning|error|danger)")
ResponseLevel = constr(regex=r"success")
ResponseFormat = constr(regex=r"(application\/json|text\/plain)")


class QueryError(BaseModel):
    """Query response model."""

    output: StrictStr = params.messages.general
    level: ErrorName = "danger"
    id: Optional[StrictStr]
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

    output: Union[Dict, StrictStr]
    level: ResponseLevel = "success"
    random: StrictStr
    cached: StrictBool
    runtime: StrictInt
    keywords: List[StrictStr] = []
    timestamp: StrictStr
    format: ResponseFormat = "text/plain"

    class Config:
        """Pydantic model configuration."""

        title = "Query Response"
        description = "Looking glass response"
        fields = {
            "level": {"title": "Level", "description": "Severity"},
            "cached": {
                "title": "Cached",
                "description": "`true` if the response is from a previously cached query.",
            },
            "random": {
                "title": "Random",
                "description": "Random string to prevent client or intermediate caching.",
                "example": "504cbdb47eb8310ca237bf512c3e10b44b0a3d85868c4b64a20037dc1c3ef857",
            },
            "runtime": {
                "title": "Runtime",
                "description": "Time it took to run the query in seconds.",
                "example": 6,
            },
            "timestamp": {
                "title": "Timestamp",
                "description": "UTC Time at which the backend application received the query.",
                "example": "2020-04-18 14:45:37",
            },
            "format": {
                "title": "Format",
                "description": "Response [MIME Type](http://www.iana.org/assignments/media-types/media-types.xhtml). Supported values: `text/plain` and `application/json`.",
                "example": "text/plain",
            },
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


class CommunityResponse(BaseModel):
    """Response model for /api/communities."""

    community: StrictStr
    display_name: StrictStr
    description: StrictStr


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


class InfoResponse(BaseModel):
    """Response model for /api/info endpoint."""

    name: StrictStr
    organization: StrictStr
    primary_asn: StrictInt
    version: StrictStr

    class Config:
        """Pydantic model configuration."""

        title = "System Information"
        description = "General information about this looking glass."
        schema_extra = {
            "examples": [
                {
                    "name": "hyperglass",
                    "organization": "Company Name",
                    "primary_asn": 65000,
                    "version": "hyperglass 1.0.0-beta.52",
                }
            ]
        }
