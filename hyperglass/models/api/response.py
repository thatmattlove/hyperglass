"""Response model."""

# Standard Library
import typing as t

# Third Party
from pydantic import Field, BaseModel, StrictInt, StrictStr, ConfigDict, StrictBool, field_validator

# Project
from hyperglass.state import use_state

ErrorName = t.Literal["success", "warning", "error", "danger"]
ResponseLevel = t.Literal["success"]
ResponseFormat = t.Literal[r"text/plain", r"application/json"]

schema_query_output = {
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
}

schema_query_level = {"title": "Level", "description": "Severity"}

schema_query_random = {
    "title": "Random",
    "description": "Random string to prevent client or intermediate caching.",
    "example": "504cbdb47eb8310ca237bf512c3e10b44b0a3d85868c4b64a20037dc1c3ef857",
}

schema_query_cached = {
    "title": "Cached",
    "description": "`true` if the response is from a previously cached query.",
}

schema_query_runtime = {
    "title": "Runtime",
    "description": "Time it took to run the query in seconds.",
    "example": 6,
}

schema_query_keywords = {
    "title": "Keywords",
    "description": "Relevant keyword values contained in the `output` field, which can be used for formatting.",
    "example": ["1.1.1.0/24", "best #1"],
}

schema_query_timestamp = {
    "title": "Timestamp",
    "description": "UTC Time at which the backend application received the query.",
    "example": "2020-04-18 14:45:37",
}

schema_query_format = {
    "title": "Format",
    "description": "Response [MIME Type](http://www.iana.org/assignments/media-types/media-types.xhtml). Supported values: `text/plain` and `application/json`.",
    "example": "text/plain",
}

schema_query_examples = [
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

schema_query_error_output = {
    "title": "Output",
    "description": "Error Details",
    "example": "192.0.2.1/32 is not allowed.",
}

schema_query_error_level = {"title": "Level", "description": "Error Severity", "example": "danger"}

schema_query_error_keywords = {
    "title": "Keywords",
    "description": "Relevant keyword values contained in the `output` field, which can be used for formatting.",
    "example": ["192.0.2.1/32"],
}


class QueryError(BaseModel):
    """Query response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Query Error",
            "description": "Response received when there is an error executing the requested query.",
            "examples": [
                {
                    "output": "192.0.2.1/32 is not allowed.",
                    "level": "danger",
                    "keywords": ["192.0.2.1/32"],
                }
            ],
        }
    )

    output: str = Field(json_schema_extra=schema_query_error_output)
    level: ErrorName = Field("danger", json_schema_extra=schema_query_error_level)
    # id: t.Optional[StrictStr]
    keywords: t.List[StrictStr] = Field([], json_schema_extra=schema_query_error_keywords)

    @field_validator("output")
    def validate_output(cls: "QueryError", value):
        """If no output is specified, use a customizable generic message."""
        if value is None:
            (messages := use_state("params").messages)
            return messages.general
        return value


class QueryResponse(BaseModel):
    """Query response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Query Response",
            "description": "Looking glass response",
            "examples": schema_query_examples,
        }
    )

    output: t.Union[t.Dict, StrictStr] = Field(json_schema_extra=schema_query_output)
    level: ResponseLevel = Field("success", json_schema_extra=schema_query_level)
    random: str = Field(json_schema_extra=schema_query_random)
    cached: bool = Field(json_schema_extra=schema_query_cached)
    runtime: int = Field(json_schema_extra=schema_query_runtime)
    keywords: t.List[str] = Field([], json_schema_extra=schema_query_keywords)
    timestamp: str = Field(json_schema_extra=schema_query_timestamp)
    format: ResponseFormat = Field("text/plain", json_schema_extra=schema_query_format)


class RoutersResponse(BaseModel):
    """Response model for /api/devices list items."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Device",
            "description": "Device attributes",
            "examples": [
                {"id": "nyc_router_1", "name": "NYC Router 1", "group": "New York City, NY"}
            ],
        }
    )

    id: StrictStr
    name: StrictStr
    group: t.Union[StrictStr, None]


class CommunityResponse(BaseModel):
    """Response model for /api/communities."""

    community: StrictStr
    display_name: StrictStr
    description: StrictStr


class SupportedQueryResponse(BaseModel):
    """Response model for /api/queries list items."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Query Type",
            "description": "If enabled is `true`, the `name` field may be used to specify the query type.",
            "examples": [{"name": "bgp_route", "display_name": "BGP Route", "enable": True}],
        }
    )

    name: StrictStr
    display_name: StrictStr
    enable: StrictBool


class InfoResponse(BaseModel):
    """Response model for /api/info endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "System Information",
            "description": "General information about this looking glass.",
            "examples": [
                {
                    "name": "hyperglass",
                    "organization": "Company Name",
                    "primary_asn": 65000,
                    "version": "hyperglass 1.0.0-beta.52",
                }
            ],
        }
    )

    name: StrictStr
    organization: StrictStr
    primary_asn: StrictInt
    version: StrictStr
