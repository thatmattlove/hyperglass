"""API Events."""

# Project
from hyperglass.log import log
from hyperglass.util import check_redis
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import REDIS_CONFIG, params


async def _check_redis():
    """Ensure Redis is running before starting server.

    Raises:
        HyperglassError: Raised if Redis is not running.

    Returns:
        {bool} -- True if Redis is running.
    """
    try:
        await check_redis(db=params.cache.database, config=REDIS_CONFIG)
    except RuntimeError as e:
        raise HyperglassError(str(e), level="danger") from None

    log.debug(f"Redis is running at: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    return True


on_startup = (_check_redis,)
on_shutdown = ()
