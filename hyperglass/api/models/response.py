"""Response model."""
# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseModel
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import constr


class QueryError(BaseModel):
    """Query response model."""

    output: StrictStr
    level: constr(regex=r"(success|warning|error|danger)")
    keywords: List[StrictStr]

    class Config:
        """Pydantic model configuration."""

        title = "Query Error"
        description = (
            "Response received when there is an error executing the requested query."
        )
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
    level: constr(regex=r"(success|warning|error|danger)")
    keywords: List[StrictStr] = []

    class Config:
        """Pydantic model configuration."""

        title = "Query Response"
        description = "Looking glass response"
        schema_extra = {
            "examples": [
                {
                    "output": """
BGP routing table entry for 1.1.1.0/24, version 224184946
BGP Bestpath: deterministic-med
Paths: (12 available, best #9, table default)
  Advertised to update-groups:
     1          40
  13335, (aggregated by 13335 172.68.129.1), (received & used)
    199.34.92.5 (metric 51) from 199.34.92.5 (199.34.92.5)
      Origin IGP, metric 0, localpref 250, valid, internal
      Community: 14525:1021 14525:2840 14525:3003 14525:4003 14525:5200 14525:5300 14525:5306
  13335, (aggregated by 13335 172.68.129.1), (received & used)
    199.34.92.6 (metric 51) from 199.34.92.6 (199.34.92.6)
      Origin IGP, metric 0, localpref 250, valid, internal
      Community: 14525:1021 14525:2840 14525:3003 14525:4003 14525:5200 14525:5300 14525:5306
  1299 13335, (aggregated by 13335 162.158.140.1)
    62.115.171.124 from 62.115.171.124 (2.255.254.51)
      Origin IGP, metric 0, localpref 100, weight 200, valid, external
      Community: 14525:0 14525:1021 14525:2840 14525:3001 14525:4001 14525:5100 14525:5103
  1299 13335, (aggregated by 13335 162.158.140.1), (received-only)
    62.115.171.124 from 62.115.171.124 (2.255.254.51)
      Origin IGP, localpref 100, valid, external
      Community: 1299:35000
  174 13335, (aggregated by 13335 108.162.239.1)
    199.34.92.7 (metric 1100) from 199.34.92.7 (199.34.92.7)
      Origin IGP, metric 0, localpref 100, weight 125, valid, internal
      Community: 14525:0 14525:840 14525:1021 14525:3004 14525:4004 14525:5100 14525:5101
  174 13335, (aggregated by 13335 108.162.239.1), (received-only)
    199.34.92.7 (metric 1100) from 199.34.92.7 (199.34.92.7)
      Origin IGP, metric 0, localpref 100, valid, internal
      Community: 14525:0 14525:840 14525:1021 14525:3004 14525:4004 14525:5100 14525:5101
  174 13335, (aggregated by 13335 162.158.140.1), (Received from a RR-client)
    199.34.92.2 (metric 26) from 199.34.92.2 (199.34.92.2)
      Origin IGP, metric 0, localpref 100, weight 200, valid, internal
      Community: 14525:0 14525:1021 14525:2840 14525:3001 14525:4001 14525:5100 14525:5101
  174 13335, (aggregated by 13335 162.158.140.1), (Received from a RR-client), (received-only)
    199.34.92.2 (metric 26) from 199.34.92.2 (199.34.92.2)
      Origin IGP, metric 0, localpref 100, valid, internal
      Community: 14525:0 14525:1021 14525:2840 14525:3001 14525:4001 14525:5100 14525:5101
  174 13335, (aggregated by 13335 162.158.140.1)
    38.140.141.25 from 38.140.141.25 (154.26.6.194)
      Origin IGP, metric 0, localpref 100, weight 200, valid, external, best
      Community: 14525:0 14525:1021 14525:2840 14525:3001 14525:4001 14525:5100 14525:5101
  174 13335, (aggregated by 13335 162.158.140.1), (received-only)
    38.140.141.25 from 38.140.141.25 (154.26.6.194)
      Origin IGP, metric 2020, localpref 100, valid, external
      Community: 174:21001 174:22013
  3257 13335, (aggregated by 13335 141.101.72.1)
    199.34.92.3 (metric 200) from 199.34.92.3 (199.34.92.3)
      Origin IGP, metric 0, localpref 100, weight 200, valid, internal
      Community: 14525:0 14525:840 14525:1021 14525:3002 14525:4002 14525:5100 14525:5104
  3257 13335, (aggregated by 13335 141.101.72.1), (received-only)
    199.34.92.3 (metric 200) from 199.34.92.3 (199.34.92.3)
      Origin IGP, metric 0, localpref 100, valid, internal
      Community: 14525:0 14525:840 14525:1021 14525:3002 14525:4002 14525:5100 14525:5104
                """,
                    "level": "success",
                    "keywords": ["1.1.1.0/24", "best #9"],
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


class Router(BaseModel):
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


class RoutersResponse(BaseModel):
    """Response model for /api/devices endpoint."""

    __root__: List[Router]

    class Config:
        """Pydantic model configuration."""

        title = "Devices"
        description = "List of all devices"


class SupportedQuery(BaseModel):
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


class SupportedQueryResponse(BaseModel):
    """Response model for /api/queries endpoint."""

    __root__: List[SupportedQuery]

    class Config:
        """Pydantic model configuration."""

        title = "Supported Query Types"
        description = "Enabled query type attributes."
