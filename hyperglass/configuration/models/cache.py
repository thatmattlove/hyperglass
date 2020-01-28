"""Validation model for Redis cache config."""

# Third Party Imports
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Cache(HyperglassModel):
    """Validation model for params.cache."""

    host: StrictStr = "localhost"
    port: StrictInt = 6379
    database: StrictInt = 0
    timeout: StrictInt = 120
    show_text: StrictBool = True
