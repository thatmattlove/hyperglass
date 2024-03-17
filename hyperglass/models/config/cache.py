"""Validation model for Redis cache config."""

# Standard Library
import typing as t

# Third Party
from pydantic import SecretStr, IPvAnyAddress

# Local
from ..main import HyperglassModel


class CachePublic(HyperglassModel):
    """Public cache parameters."""

    timeout: int = 120
    show_text: bool = True


class Cache(CachePublic):
    """Validation model for params.cache."""

    host: t.Union[IPvAnyAddress, str] = "localhost"
    port: int = 6379
    database: int = 1
    password: t.Optional[SecretStr] = None
