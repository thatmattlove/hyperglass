"""Response model."""

# Standard Library
# flake8: noqa
import math
import secrets
from typing import List, Union, Optional
from datetime import datetime

# Third Party
from pydantic import BaseModel, StrictInt, StrictStr, StrictFloat, constr, validator


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


class _HyperglassQuery(BaseModel):
    class Config:
        validate_all = True
        validate_assignment = True


class BaseQuery(_HyperglassQuery):
    protocol: StrictStr = "1,1"
    router: StrictStr
    routerindex: StrictInt
    random: StrictStr = secrets.token_urlsafe(16)
    vrf: Optional[StrictStr]
    runtime: StrictInt = 30
    query_format: constr(regex=r"(text\/plain|application\/json)") = "text/plain"

    @validator("runtime")
    def validate_runtime(cls, value):
        if isinstance(value, float) and math.modf(value)[0] == 0:
            value = math.ceil(value)
        return value

    class Config:
        fields = {"query_format": "format"}


class BaseData(_HyperglassQuery):
    router: StrictStr
    performed_at: datetime
    runtime: Union[StrictFloat, StrictInt]
    output: List[StrictStr]
    data_format: StrictStr

    @validator("runtime")
    def validate_runtime(cls, value):
        if isinstance(value, float) and math.modf(value)[0] == 0:
            value = math.ceil(value)
        return value

    class Config:
        fields = {"data_format": "format"}
        extra = "allow"


class QueryError(_HyperglassQuery):
    status: constr(regex=r"error")
    message: StrictStr


class QueryResponse(_HyperglassQuery):
    status: constr(regex=r"success|fail")
    data: BaseData
