"""Response model."""
# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseModel
from pydantic import StrictStr
from pydantic import constr


class QueryResponse(BaseModel):
    """Query response model."""

    output: StrictStr
    alert: constr(regex=r"(warning|error|danger)")
    keywords: List[StrictStr]
