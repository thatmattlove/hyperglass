"""Utility fuctions."""

# Third Party Imports
from loguru import logger as _loguru_logger

# Project Imports
from hyperglass.constants import LOG_HANDLER
from hyperglass.constants import LOG_LEVELS
from hyperglass.exceptions import ConfigInvalid

_loguru_logger.remove()
_loguru_logger.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)

log = _loguru_logger


async def check_redis(host, port):
    """Validate if Redis is running.

    Arguments:
        host {str} -- IP address or hostname of Redis server
        port {[type]} -- TCP port of Redis server

    Raises:
        ConfigInvalid: Raised if redis server is unreachable

    Returns:
        {bool} -- True if running, False if not
    """
    import asyncio
    from socket import gaierror

    try:
        _reader, _writer = await asyncio.open_connection(str(host), int(port))
    except gaierror:
        raise ConfigInvalid(
            "Redis isn't running: {host}:{port} is unreachable/unresolvable.",
            alert="danger",
            host=host,
            port=port,
        )
    if _reader or _writer:
        return True
    else:
        return False
