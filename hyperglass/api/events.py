"""API Events."""

# Standard Library
import typing as t

# Third Party
from litestar import Litestar

# Project
from hyperglass.state import use_state

__all__ = ("check_redis",)


async def check_redis(_: Litestar) -> t.NoReturn:
    """Ensure Redis is running before starting server."""
    cache = use_state("cache")
    cache.check()
