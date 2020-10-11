"""API Events."""

# Project
from hyperglass.cache import AsyncCache
from hyperglass.configuration import REDIS_CONFIG, params


async def check_redis() -> bool:
    """Ensure Redis is running before starting server."""
    cache = AsyncCache(db=params.cache.database, **REDIS_CONFIG)
    await cache.test()
    return True


on_startup = (check_redis,)
on_shutdown = ()
