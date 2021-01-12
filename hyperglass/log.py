"""Logging instance setup & configuration."""

# Standard Library
import os
import sys
import logging
from datetime import datetime

# Third Party
from loguru import logger as _loguru_logger

_FMT = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw> {name}<lw>:</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)
_DATE_FMT = "%Y%m%d %H:%M:%S"
_FMT_BASIC = "{message}"
_LOG_LEVELS = [
    {"name": "TRACE", "no": 5, "color": "<m>"},
    {"name": "DEBUG", "no": 10, "color": "<c>"},
    {"name": "INFO", "no": 20, "color": "<le>"},
    {"name": "SUCCESS", "no": 25, "color": "<g>"},
    {"name": "WARNING", "no": 30, "color": "<y>"},
    {"name": "ERROR", "no": 40, "color": "<y>"},
    {"name": "CRITICAL", "no": 50, "color": "<r>"},
]


def setup_lib_logging() -> None:
    """Override the logging handlers for dependency libraries."""
    for name in (
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.asgi",
        "netmiko",
        "scrapli",
        "httpx",
    ):
        _loguru_logger.bind(logger_name=name)


def base_logger(level: str = "INFO"):
    """Initialize hyperglass logging instance."""
    _loguru_logger.remove()
    _loguru_logger.add(sys.stdout, format=_FMT, level=level, enqueue=True)
    _loguru_logger.configure(levels=_LOG_LEVELS)
    return _loguru_logger


log = base_logger()

logging.addLevelName(25, "SUCCESS")


def _log_success(self, message, *a, **kw):
    """Add custom builtin logging handler for the success level."""
    if self.isEnabledFor(25):
        self._log(25, message, a, **kw)


logging.Logger.success = _log_success


def set_log_level(logger, debug):
    """Set log level based on debug state."""
    if debug:
        os.environ["HYPERGLASS_LOG_LEVEL"] = "DEBUG"
        base_logger("DEBUG")

    if debug:
        logger.debug("Debugging enabled")
    return True


def enable_file_logging(logger, log_directory, log_format, log_max_size):
    """Set up file-based logging from configuration parameters."""

    if log_format == "json":
        log_file_name = "hyperglass.log.json"
        structured = True
    else:
        log_file_name = "hyperglass.log"
        structured = False

    log_file = log_directory / log_file_name

    if log_format == "text":
        now_str = "hyperglass logs for " + datetime.utcnow().strftime(
            "%B %d, %Y beginning at %H:%M:%S UTC"
        )
        now_str_y = len(now_str) + 6
        now_str_x = len(now_str) + 4
        log_break = (
            "#" * now_str_y,
            "\n#" + " " * now_str_x + "#\n",
            "#  ",
            now_str,
            "  #",
            "\n#" + " " * now_str_x + "#\n",
            "#" * now_str_y,
        )

        with log_file.open("a+") as lf:
            lf.write(f'\n\n{"".join(log_break)}\n\n')

    logger.add(
        log_file,
        format=_FMT,
        rotation=log_max_size,
        serialize=structured,
        enqueue=True,
    )

    logger.debug("Logging to {} enabled", str(log_file))

    return True


def enable_syslog_logging(logger, syslog_host, syslog_port):
    """Set up syslog logging from configuration parameters."""

    # Standard Library
    from logging.handlers import SysLogHandler

    logger.add(
        SysLogHandler(address=(str(syslog_host), syslog_port)),
        format=_FMT_BASIC,
        enqueue=True,
    )
    logger.debug(
        "Logging to syslog target {}:{} enabled", str(syslog_host), str(syslog_port),
    )
    return True
