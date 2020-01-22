"""API Events."""
# Third Party Imports
from starlette.exceptions import HTTPException

# Project Imports
from hyperglass.configuration import URL_DEV
from hyperglass.configuration import URL_PROD
from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.query import REDIS_CONFIG
from hyperglass.util import build_frontend
from hyperglass.util import check_python
from hyperglass.util import check_redis
from hyperglass.util import clear_redis_cache
from hyperglass.util import log


async def check_python_version():
    """Ensure Python version meets minimum requirement.

    Raises:
        HyperglassError: Raised if Python version is invalid.
    """
    try:
        python_version = check_python()
        log.info(f"Python {python_version} detected")
    except RuntimeError as r:
        raise HyperglassError(str(r), alert="danger") from None


async def check_redis_instance():
    """Ensure Redis is running before starting server.

    Raises:
        HyperglassError: Raised if Redis is not running.

    Returns:
        {bool} -- True if Redis is running.
    """
    try:
        await check_redis(db=params.features.cache.redis_id, config=REDIS_CONFIG)
    except RuntimeError as e:
        raise HyperglassError(str(e), alert="danger") from None

    log.debug(f"Redis is running at: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    return True


async def build_ui():
    """Perform a UI build prior to starting the application.

    Raises:
        HTTPException: Raised if any build errors occur.

    Returns:
        {bool} -- True if successful.
    """
    try:
        await build_frontend(
            dev_mode=params.general.developer_mode,
            dev_url=URL_DEV,
            prod_url=URL_PROD,
            params=frontend_params,
        )
    except RuntimeError as e:
        raise HTTPException(detail=str(e), status_code=500)
    return True


async def clear_cache():
    """Clear the Redis cache on shutdown."""
    try:
        await clear_redis_cache(db=params.features.cache.redis_id, config=REDIS_CONFIG)
    except RuntimeError as e:
        log.error(str(e))
        pass


on_startup = [check_python_version, check_redis_instance, build_ui]
on_shutdown = [clear_cache]
