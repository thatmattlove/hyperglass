"""Validation model for Redis cache config."""

# Standard Library Imports
from typing import Union

# Third Party Imports
from pydantic import Field
from pydantic import IPvAnyAddress
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Cache(HyperglassModel):
    """Validation model for params.cache."""

    host: Union[IPvAnyAddress, StrictStr] = Field(
        "localhost", title="Host", description="Redis server IP address or hostname."
    )
    port: StrictInt = Field(6379, title="Port", description="Redis server TCP port.")
    database: StrictInt = Field(
        0, title="Database ID", description="Redis server database ID."
    )
    timeout: StrictInt = Field(
        120,
        title="Timeout",
        description="Time in seconds query output will be kept in the Redis cache.",
    )
    show_text: StrictBool = Field(
        True,
        title="Show Text",
        description="Show the [`cache`](/fixme) text in the hyperglass UI.",
    )

    class Config:
        """Pydantic model configuration."""

        title = "Cache"
        description = "Redis server & cache timeout configuration."
