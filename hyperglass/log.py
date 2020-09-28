"""Logging instance setup & configuration."""

# Standard Library
import os
import logging
from datetime import datetime

# Third Party
from loguru import logger as _loguru_logger
from rich.theme import Theme
from rich.console import Console
from rich.logging import RichHandler

_FMT_FILE = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw> {name}<lw>:</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)
_DATE_FMT = "%Y%m%d %H:%M:%S"
_FMT_STDOUT = "{message}"
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

_RICH_THEME = Theme(
    {
        "logging.level.debug": "bold grey50",
        "logging.level.info": "bold blue",
        "logging.level.success": "bold green",
        "logging.level.warning": "bold yellow",
        "logging.level.error": "bold dark_goldenrod",
        "logging.level.critical": "bold red",
    }
)

_RICH_CONSOLE = Console(theme=_RICH_THEME, log_time_format=_DATE_FMT)


def _get_rich(debug: bool = False) -> RichHandler:
    rich_kwargs = {
        "level": "INFO",
        "markup": True,
        "rich_tracebacks": True,
        "console": _RICH_CONSOLE,
    }
    if debug:
        rich_kwargs["level"] = "DEBUG"
    return RichHandler(**rich_kwargs)


def base_logger():
    """Initialize hyperglass logging instance."""
    _loguru_logger.remove()
    _loguru_logger.add(_get_rich(), format=_FMT_BASIC, level="INFO", enqueue=True)
    _loguru_logger.configure(levels=_LOG_LEVELS)
    return _loguru_logger


log = base_logger()

logging.addLevelName(25, "SUCCESS")


def _log_success(self, message, *a, **kw):
    """Add custom builtin logging handler for the success level."""
    if self.isEnabledFor(25):
        self._log(25, message, a, **kw)


logging.Logger.success = _log_success

builtin_logging_config = {
    "version": 1,
    "formatters": {"basic": {"format": "%(message)s"}},
    "root": {"level": "INFO", "handlers": ["rich"]},
    "handlers": {
        "rich": {
            "level": "INFO",
            "formatter": "basic",
            "class": "rich.logging.RichHandler",
        },
        "console": {
            "level": "INFO",
            "formatter": "basic",
            "class": "rich.logging.RichHandler",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "uvicorn": {"handlers": ["rich"], "level": "INFO", "propagate": True},
        "uvicorn.access": {"handlers": ["rich"], "level": "INFO", "propagate": True},
        "uvicorn.error": {"handlers": ["rich"], "level": "ERROR", "propagate": True},
        "uvicorn.asgi": {"handlers": ["rich"], "level": "INFO", "propagate": True},
    },
}


def set_log_level(logger, debug):
    """Set log level based on debug state."""
    if debug:
        os.environ["HYPERGLASS_LOG_LEVEL"] = "DEBUG"
        logger.remove()
        logger.add(_get_rich(True), format=_FMT_BASIC, level="DEBUG", enqueue=True)
        logger.configure(levels=_LOG_LEVELS)

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
        format=_FMT_FILE,
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
