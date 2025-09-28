"""API Events."""

# Standard Library
import typing as t

# Third Party
from litestar import Litestar

# Project
from hyperglass.state import use_state
from hyperglass.log import log

__all__ = ("check_redis", "init_ip_enrichment")


async def check_redis(_: Litestar) -> t.NoReturn:
    """Ensure Redis is running before starting server."""
    cache = use_state("cache")
    cache.check()


async def init_ip_enrichment(_: Litestar) -> None:
    """Initialize IP enrichment data at startup."""
    try:
        params = use_state("params")
        if not params.structured.ip_enrichment.enabled:
            log.debug("IP enrichment disabled, skipping initialization")
            return
    except Exception as e:
        log.debug(f"Could not check IP enrichment config: {e}")
        return

    try:
        from hyperglass.external.ip_enrichment import _service

        log.info("Initializing IP enrichment data at startup...")
        success = await _service.ensure_data_loaded()
        if success:
            log.info("IP enrichment data loaded successfully at startup")
        else:
            log.warning("Failed to load IP enrichment data at startup")
    except Exception as e:
        log.error(f"Error initializing IP enrichment data: {e}")
