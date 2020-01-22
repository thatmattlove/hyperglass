"""Response model."""
# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseModel
from pydantic import StrictStr
from pydantic import constr


class QueryError(BaseModel):
    """Query response model."""

    output: StrictStr
    level: constr(regex=r"(success|warning|error|danger)")
    keywords: List[StrictStr]


class QueryResponse(BaseModel):
    """Query response model."""

    output: StrictStr
    level: constr(regex=r"(success|warning|error|danger)")
    keywords: List[StrictStr] = []
