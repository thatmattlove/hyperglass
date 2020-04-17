"""Validation model for Redis cache config."""

# Standard Library
from typing import Union

# Third Party
from pydantic import Field, StrictInt, StrictStr, StrictBool, IPvAnyAddress

# Project
from hyperglass.models import HyperglassModel


class Cache(HyperglassModel):
    """Validation model for params.cache."""

    host: Union[IPvAnyAddress, StrictStr] = Field(
        "localhost", title="Host", description="Redis server IP address or hostname."
    )
    port: StrictInt = Field(6379, title="Port", description="Redis server TCP port.")
    database: StrictInt = Field(
        1, title="Database ID", description="Redis server database ID."
    )
    timeout: StrictInt = Field(
        120,
        title="Timeout",
        description="Time in seconds query output will be kept in the Redis cache.",
    )
    show_text: StrictBool = Field(
        True,
        title="Show Text",
        description="Show the cache text in the hyperglass UI.",
    )

    class Config:
        """Pydantic model configuration."""

        title = "Cache"
        description = "Redis server & cache timeout configuration."
