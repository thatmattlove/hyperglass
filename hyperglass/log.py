"""Logging instance setup & configuration."""

# Standard Library
import sys
import typing as t
import logging
from datetime import datetime

# Third Party
from loguru import logger as _loguru_logger
from rich.logging import RichHandler
from gunicorn.glogging import Logger as GunicornLogger  # type: ignore

# Local
from .constants import __version__

if t.TYPE_CHECKING:
    # Standard Library
    from pathlib import Path

    # Third Party
    from loguru import Logger as LoguruLogger
    from pydantic import ByteSize

    # Project
    from hyperglass.models.fields import LogFormat

_FMT = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw> {name}<lw>:</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)

_FMT_FILE = "[{time:YYYYMMDD} {time:HH:mm:ss}] {message}"
_DATE_FMT = "%Y%m%d %H:%M:%S"
_FMT_BASIC = "{message}"
_LOG_LEVELS = [
    {"name": "TRACE", "color": "<m>"},
    {"name": "DEBUG", "color": "<c>"},
    {"name": "INFO", "color": "<le>"},
    {"name": "SUCCESS", "color": "<g>"},
    {"name": "WARNING", "color": "<y>"},
    {"name": "ERROR", "color": "<y>"},
    {"name": "CRITICAL", "color": "<r>"},
]


class LibIntercentHandler(logging.Handler):
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


class CustomGunicornLogger(GunicornLogger):
    """Custom logger to direct Gunicorn/Uvicorn logs to Loguru.

    See: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    """

    def setup(self, cfg: t.Any) -> None:
        """Override Gunicorn setup."""
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(cfg.loglevel)
        self.access_logger.setLevel(cfg.loglevel)


def setup_lib_logging(log_level: str) -> None:
    """Override the logging handlers for dependency libraries.

    See: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    """

    intercept_handler = LibIntercentHandler()

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.asgi",
        "netmiko",
        "paramiko",
        "scrapli",
        "httpx",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]


def _log_patcher(record):
    """Patch for exception handling in logger.

    See: https://github.com/Delgan/loguru/issues/504
    """
    exception = record["exception"]
    if exception is not None:
        fixed = Exception(str(exception.value))
        record["exception"] = exception._replace(value=fixed)


def init_logger(level: str = "INFO"):
    """Initialize hyperglass logging instance."""

    # Reset built-in Loguru configurations.
    _loguru_logger.remove()

    if sys.stdout.isatty():
        # Use Rich for logging if hyperglass started from a TTY.
        _loguru_logger.add(
            sink=RichHandler(
                rich_tracebacks=True,
                level=level,
                tracebacks_show_locals=True,
                log_time_format="[%Y%m%d %H:%M:%S]",
            ),
            format=_FMT_BASIC,
            level=level,
            enqueue=True,
        )
    else:
        # Otherwise, use regular format.
        _loguru_logger.add(sys.stdout, format=_FMT, level=level, enqueue=True)

    _loguru_logger.configure(levels=_LOG_LEVELS, patcher=_log_patcher)

    return _loguru_logger


log = init_logger()

logging.addLevelName(25, "SUCCESS")


def _log_success(self: "LoguruLogger", message: str, *a: t.Any, **kw: t.Any) -> None:
    """Add custom builtin logging handler for the success level."""
    if self.isEnabledFor(25):
        self._log(25, message, a, **kw)


logging.Logger.success = _log_success


def enable_file_logging(
    log_directory: "Path", log_format: "LogFormat", log_max_size: "ByteSize", debug: bool
) -> None:
    """Set up file-based logging from configuration parameters."""

    log_level = "DEBUG" if debug else "INFO"

    if log_format == "json":
        log_file_name = "hyperglass.log.json"
        structured = True
    else:
        log_file_name = "hyperglass.log"
        structured = False

    log_file = log_directory / log_file_name

    if log_format == "text":
        now_str = datetime.utcnow().strftime("%B %d, %Y beginning at %H:%M:%S UTC")
        header_lines = (
            f"# {line}"
            for line in (
                f"hyperglass {__version__}",
                f"Logs for {now_str}",
                f"Log Level: {log_level}",
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
        level=log_level,
        encoding="utf8",
        rotation=log_max_size.human_readable(),
    )
    log.debug("Logging to file {!s}", log_file)


def enable_syslog_logging(syslog_host: str, syslog_port: int) -> None:
    """Set up syslog logging from configuration parameters."""

    # Standard Library
    from logging.handlers import SysLogHandler

    _loguru_logger.add(
        SysLogHandler(address=(str(syslog_host), syslog_port)), format=_FMT_BASIC, enqueue=True,
    )
    log.debug(
        "Logging to syslog target {}:{} enabled", str(syslog_host), str(syslog_port),
    )
