"""Logging instance setup & configuration."""

# Standard Library
import os
import sys
from datetime import datetime

# Third Party
from loguru import logger as _loguru_logger

_LOG_FMT = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw> {name}<lw>:</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)
_LOG_LEVELS = [
    {"name": "TRACE", "no": 5, "color": "<m>"},
    {"name": "DEBUG", "no": 10, "color": "<c>"},
    {"name": "INFO", "no": 20, "color": "<le>"},
    {"name": "SUCCESS", "no": 25, "color": "<g>"},
    {"name": "WARNING", "no": 30, "color": "<y>"},
    {"name": "ERROR", "no": 40, "color": "<y>"},
    {"name": "CRITICAL", "no": 50, "color": "<r>"},
]


def base_logger():
    """Initialize hyperglass logging instance."""
    _loguru_logger.remove()
    _loguru_logger.add(sys.stdout, format=_LOG_FMT, level="INFO", enqueue=True)
    _loguru_logger.configure(levels=_LOG_LEVELS)
    return _loguru_logger


log = base_logger()


def set_log_level(logger, debug):
    """Set log level based on debug state."""
    if debug:
        os.environ["HYPERGLASS_LOG_LEVEL"] = "DEBUG"
        logger.remove()
        logger.add(sys.stdout, format=_LOG_FMT, level="DEBUG", enqueue=True)
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

    logger.add(log_file, rotation=log_max_size, serialize=structured, enqueue=True)

    logger.debug("Logging to file enabled")

    return True


def enable_syslog_logging(logger, syslog_host, syslog_port):
    """Set up syslog logging from configuration parameters."""
    from logging.handlers import SysLogHandler

    logger.add(
        SysLogHandler(address=(str(syslog_host), syslog_port)),
        format="{message}",
        enqueue=True,
    )
    logger.debug(
        "Logging to syslog target {h}:{p} enabled",
        h=str(syslog_host),
        p=str(syslog_port),
    )
    return True
