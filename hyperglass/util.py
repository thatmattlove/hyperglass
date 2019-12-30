"""Utility fuctions."""


def _logger():
    from loguru import logger as _loguru_logger
    from hyperglass.constants import LOG_HANDLER
    from hyperglass.constants import LOG_LEVELS

    _loguru_logger.remove()
    _loguru_logger.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)
    return _loguru_logger


def cpu_count():
    """Get server's CPU core count.

    Used for number of web server workers.

    Returns:
        {int} -- CPU Cores
    """
    import multiprocessing

    return multiprocessing.cpu_count()


log = _logger()
