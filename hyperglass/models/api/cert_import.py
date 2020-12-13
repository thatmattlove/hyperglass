"""hyperglass-agent certificate import models."""
# Standard Library
from typing import Union

# Third Party
from pydantic import BaseModel, StrictStr

# Local
from ..fields import StrictBytes


class EncodedRequest(BaseModel):
    """Certificate request model."""

    device: StrictStr
    encoded: Union[StrictStr, StrictBytes]
