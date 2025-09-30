"""API Events."""

# Standard Library
import typing as t

# Third Party
from litestar import Litestar

# Project
from hyperglass.state import use_state
from hyperglass.log import log

__all__ = ("check_redis",)


async def check_redis(_: Litestar) -> t.NoReturn:
    """Ensure Redis is running before starting server."""
    cache = use_state("cache")
    cache.check()


# init_ip_enrichment removed: startup refresh is intentionally disabled and
# IP enrichment data is loaded on-demand when required. Keeping a no-op
# startup hook adds no value and may cause confusion.
