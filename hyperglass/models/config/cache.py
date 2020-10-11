"""Validation model for Redis cache config."""

# Standard Library
from typing import Union, Optional

# Third Party
from pydantic import SecretStr, StrictInt, StrictStr, StrictBool, IPvAnyAddress

# Local
from ..main import HyperglassModel


class Cache(HyperglassModel):
    """Validation model for params.cache."""

    host: Union[IPvAnyAddress, StrictStr] = "localhost"
    port: StrictInt = 6379
    database: StrictInt = 1
    password: Optional[SecretStr]
    timeout: StrictInt = 120
    show_text: StrictBool = True

    class Config:
        """Pydantic model configuration."""

        title = "Cache"
        description = "Redis server & cache timeout configuration."
        fields = {
            "host": {"description": "Redis server IP address or hostname."},
            "port": {"description": "Redis server TCP port."},
            "database": {"description": "Redis server database ID."},
            "password": {"description": "Redis authentication password."},
            "timeout": {
                "description": "Time in seconds query output will be kept in the Redis cache."
            },
            "show_test": {description: "Show the cache text in the hyperglass UI."},
        }
