"""Response model."""

# Standard Library
# flake8: noqa
import math
import typing as t
import secrets
from datetime import datetime

# Third Party
from pydantic import Field, BaseModel, ConfigDict, field_validator

"""Patterns:
GET /.well-known/looking-glass/v1/ping/2001:DB8::35?protocol=2,1
GET /.well-known/looking-glass/v1/traceroute/192.0.2.8?routerindex=5
GET /.well-known/looking-glass/v1/show/route/2001:DB8::/48?protocol=2,1
GET /.well-known/looking-glass/v1/show/bgp/192.0.2.0/24
GET /.well-known/looking-glass/v1/show/bgp/summary?protocol=2&routerindex=3
GET /.well-known/looking-glass/v1/show/bgp/neighbors/192.0.2.226
GET /.well-known/looking-glass/v1/routers
GET /.well-known/looking-glass/v1/routers/1
GET /.well-known/looking-glass/v1/cmd
"""

QueryFormat = t.Literal[r"text/plain", r"application/json"]


class _HyperglassQuery(BaseModel):
    model_config = ConfigDict(validate_assignment=True, validate_default=True)


class BaseQuery(_HyperglassQuery):
    protocol: str = "1,1"
    router: str
    routerindex: int
    random: str = secrets.token_urlsafe(16)
    runtime: int = 30
    query_format: QueryFormat = Field("text/plain", alias="format")

    @field_validator("runtime")
    def validate_runtime(cls, value):
        if isinstance(value, float) and math.modf(value)[0] == 0:
            value = math.ceil(value)
        return value


class BaseData(_HyperglassQuery):
    model_config = ConfigDict(extra="allow")

    router: str
    performed_at: datetime
    runtime: t.Union[float, int]
    output: t.List[str]
    data_format: str = Field(alias="format")

    @field_validator("runtime")
    def validate_runtime(cls, value):
        if isinstance(value, float) and math.modf(value)[0] == 0:
            value = math.ceil(value)
        return value


class QueryError(_HyperglassQuery):
    status: t.Literal["error"]
    message: str


class QueryResponse(_HyperglassQuery):
    status: t.Literal["success", "fail"]
    data: BaseData
