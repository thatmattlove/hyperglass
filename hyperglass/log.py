"""Logging instance setup & configuration."""

# Standard Library
import sys
import typing as t
import logging
from datetime import datetime

# Third Party
from loguru import logger as _loguru_logger
from rich.theme import Theme
from rich.console import Console
from rich.logging import RichHandler

# Local
from .util import dict_to_kwargs
from .constants import __version__

if t.TYPE_CHECKING:
    # Standard Library
    from pathlib import Path

    # Third Party
    from loguru import Logger as Record
    from pydantic import ByteSize

    # Project
    from hyperglass.models.fields import LogFormat

_FMT_DEBUG = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message} {extra}"
)

_FMT = "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw></lvl> {message} {extra}"

_FMT_FILE = "[{time:YYYYMMDD} {time:HH:mm:ss}] {message} {extra}"
_FMT_BASIC = "{message} {extra}"
_LOG_LEVELS = [
    {"name": "TRACE", "color": "<m>"},
    {"name": "DEBUG", "color": "<c>"},
    {"name": "INFO", "color": "<le>"},
    {"name": "SUCCESS", "color": "<g>"},
    {"name": "WARNING", "color": "<y>"},
    {"name": "ERROR", "color": "<y>"},
    {"name": "CRITICAL", "color": "<r>"},
]

_EXCLUDE_MODULES = (
    "PIL",
    "svglib",
    "paramiko.transport",
)

HyperglassConsole = Console(
    theme=Theme(
        {
            "info": "bold cyan",
            "warning": "bold yellow",
            "error": "bold red",
            "success": "bold green",
            "critical": "bold bright_red",
            "logging.level.info": "bold cyan",
            "logging.level.warning": "bold yellow",
            "logging.level.error": "bold red",
            "logging.level.critical": "bold bright_red",
            "logging.level.success": "bold green",
            "subtle": "rgb(128,128,128)",
        }
    )
)

log = _loguru_logger


def formatter(record: "Record") -> str:
    """Format log messages with extra data as kwargs string."""
    msg = record.get("message", "")
    extra = record.get("extra", {})
    extra_str = dict_to_kwargs(extra)
    return " ".join((msg, extra_str))


def filter_uvicorn_values(record: "Record") -> bool:
    """Drop noisy uvicorn messages."""
    drop = (
        "Application startup",
        "Application shutdown",
        "Finished server process",
        "Shutting down",
        "Waiting for application",
        "Started server process",
        "Started parent process",
        "Stopping parent process",
    )
    for match in drop:
        if match in record["message"]:
            return False
    return True


class LibInterceptHandler(logging.Handler):
    """Custom log handler for integrating third party library logging with hyperglass's logger."""

    def emit(self, record):
        """Emit log record.

        See: https://github.com/Delgan/loguru (Readme)
        """
        # Get corresponding Loguru level if it exists
        try:
            level = _loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        _loguru_logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logger(level: t.Union[int, str] = logging.INFO):
    """Initialize hyperglass logging instance."""

    for mod in _EXCLUDE_MODULES:
        logging.getLogger(mod).propagate = False

    # Reset built-in Loguru configurations.
    _loguru_logger.remove()

    if sys.stdout.isatty():
        # Use Rich for logging if hyperglass started from a TTY.

        _loguru_logger.add(
            sink=RichHandler(
                console=HyperglassConsole,
                rich_tracebacks=True,
                tracebacks_show_locals=level == logging.DEBUG,
                log_time_format="[%Y%m%d %H:%M:%S]",
            ),
            format=formatter,
            colorize=False,
            level=level,
            filter=filter_uvicorn_values,
            enqueue=True,
        )
    else:
        # Otherwise, use regular format.
        _loguru_logger.add(
            sink=sys.stdout,
            enqueue=True,
            format=_FMT if level == logging.INFO else _FMT_DEBUG,
            level=level,
            colorize=False,
            filter=filter_uvicorn_values,
        )

    _loguru_logger.configure(levels=_LOG_LEVELS)

    return _loguru_logger


def enable_file_logging(
    *,
    directory: "Path",
    log_format: "LogFormat",
    max_size: "ByteSize",
    level: t.Union[str, int],
) -> None:
    """Set up file-based logging from configuration parameters."""

    if log_format == "json":
        log_file_name = "hyperglass.log.json"
        structured = True
    else:
        log_file_name = "hyperglass.log"
        structured = False

    log_file = directory / log_file_name

    if log_format == "text":
        now_str = datetime.utcnow().strftime("%B %d, %Y beginning at %H:%M:%S UTC")
        header_lines = (
            f"# {line}"
            for line in (
                f"hyperglass {__version__}",
                f"Logs for {now_str}",
                f"Log Level: {'INFO' if level == logging.INFO else 'DEBUG'}",
            )
        )
        header = "\n" + "\n".join(header_lines) + "\n"

        with log_file.open("a+") as lf:
            lf.write(header)

    _loguru_logger.add(
        enqueue=True,
        sink=log_file,
        format=_FMT_FILE,
        serialize=structured,
        level=level,
        encoding="utf8",
        colorize=False,
        rotation=max_size.human_readable(),
    )
    _loguru_logger.bind(path=log_file).debug("Logging to file")


def enable_syslog_logging(*, host: str, port: int) -> None:
    """Set up syslog logging from configuration parameters."""

    # Standard Library
    from logging.handlers import SysLogHandler

    _loguru_logger.add(
        SysLogHandler(address=(str(host), port)),
        format=_FMT_BASIC,
        enqueue=True,
        colorize=False,
    )
    _loguru_logger.bind(host=host, port=port).debug("Logging to syslog target")
