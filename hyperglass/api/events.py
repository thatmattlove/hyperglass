"""API Events."""
# Third Party
from starlette.exceptions import HTTPException

# Project
from hyperglass.util import (
    log,
    check_redis,
    check_python,
    build_frontend,
    clear_redis_cache,
)
from hyperglass.constants import MIN_PYTHON_VERSION
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import (
    URL_DEV,
    URL_PROD,
    CONFIG_PATH,
    REDIS_CONFIG,
    params,
    frontend_params,
)


async def check_python_version():
    """Ensure Python version meets minimum requirement.

    Raises:
        HyperglassError: Raised if Python version is invalid.
    """
    try:
        python_version = check_python()
        required = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
        log.info(f"Python {python_version} detected ({required} required)")
    except RuntimeError as e:
        raise HyperglassError(str(e), level="danger") from None


async def check_redis_instance():
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


async def build_ui():
    """Perform a UI build prior to starting the application.

    Raises:
        HTTPException: Raised if any build errors occur.

    Returns:
        {bool} -- True if successful.
    """
    try:
        await build_frontend(
            dev_mode=params.developer_mode,
            dev_url=URL_DEV,
            prod_url=URL_PROD,
            params=frontend_params,
            app_path=CONFIG_PATH,
        )
    except RuntimeError as e:
        raise HTTPException(detail=str(e), status_code=500)
    return True


async def clear_cache():
    """Clear the Redis cache on shutdown."""
    try:
        await clear_redis_cache(db=params.cache.database, config=REDIS_CONFIG)
    except RuntimeError as e:
        log.error(str(e))
        pass


on_startup = [check_python_version, check_redis_instance, build_ui]
on_shutdown = [clear_cache]
