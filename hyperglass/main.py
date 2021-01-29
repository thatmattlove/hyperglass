"""Gunicorn Config File."""

# Standard Library
import sys
import math
import shutil
import logging
import platform

# Third Party
from gunicorn.arbiter import Arbiter
from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger

# Local
from .log import log, setup_lib_logging
from .constants import MIN_NODE_VERSION, MIN_PYTHON_VERSION, __version__
from .util.frontend import get_node_version

# Ensure the Python version meets the minimum requirements.
pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
if sys.version_info < MIN_PYTHON_VERSION:
    raise RuntimeError(f"Python {pretty_version}+ is required.")

# Ensure the NodeJS version meets the minimum requirements.
node_version = get_node_version()

if node_version != MIN_NODE_VERSION:
    raise RuntimeError(f"NodeJS {MIN_NODE_VERSION}+ is required.")


# Project
from hyperglass.compat._asyncio import aiorun

# Local
from .util import cpu_count, clear_redis_cache, format_listen_address
from .cache import SyncCache
from .configuration import (
    URL_DEV,
    URL_PROD,
    CONFIG_PATH,
    REDIS_CONFIG,
    params,
    frontend_params,
)
from .util.frontend import build_frontend

if params.debug:
    workers = 1
    loglevel = "DEBUG"
else:
    workers = cpu_count(2)
    loglevel = "WARNING"


class StubbedGunicornLogger(Logger):
    """Custom logging to direct Gunicorn/Uvicorn logs to Loguru/Rich.

    See: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    """

    def setup(self, cfg):
        """Override Gunicorn setup."""
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(loglevel)
        self.access_logger.setLevel(loglevel)


def check_redis_instance() -> bool:
    """Ensure Redis is running before starting server."""

    cache = SyncCache(db=params.cache.database, **REDIS_CONFIG)
    cache.test()
    log.debug("Redis is running at: {}:{}", REDIS_CONFIG["host"], REDIS_CONFIG["port"])
    return True


async def build_ui() -> bool:
    """Perform a UI build prior to starting the application."""
    await build_frontend(
        dev_mode=params.developer_mode,
        dev_url=URL_DEV,
        prod_url=URL_PROD,
        params=frontend_params,
        app_path=CONFIG_PATH,
    )
    return True


async def clear_cache():
    """Clear the Redis cache on shutdown."""
    try:
        await clear_redis_cache(db=params.cache.database, config=REDIS_CONFIG)
    except RuntimeError as e:
        log.error(str(e))
        pass


def cache_config() -> bool:
    """Add configuration to Redis cache as a pickled object."""
    # Standard Library
    import pickle

    cache = SyncCache(db=params.cache.database, **REDIS_CONFIG)
    cache.set("HYPERGLASS_CONFIG", pickle.dumps(params))

    return True


def on_starting(server: Arbiter):
    """Gunicorn pre-start tasks."""

    setup_lib_logging()

    python_version = platform.python_version()
    required = ".".join((str(v) for v in MIN_PYTHON_VERSION))
    log.info("Python {} detected ({} required)", python_version, required)

    async def runner():
        # Standard Library
        from asyncio import gather

        await gather(build_ui(), cache_config())

    check_redis_instance()
    aiorun(build_ui())
    cache_config()

    log.success(
        "Started hyperglass {v} on http://{h}:{p} with {w} workers",
        v=__version__,
        h=format_listen_address(params.listen_address),
        p=str(params.listen_port),
        w=server.app.cfg.settings["workers"].value,
    )


def on_exit(server: Arbiter):
    """Gunicorn shutdown tasks."""

    log.critical("Stopping hyperglass {}", __version__)

    async def runner():
        if not params.developer_mode:
            await clear_cache()

    aiorun(runner())


class HyperglassWSGI(BaseApplication):
    """Custom gunicorn app."""

    def __init__(self, app, options):
        """Initialize custom WSGI."""
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        """Load gunicorn config."""
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load gunicorn app."""
        return self.application


def start(**kwargs):
    """Start hyperglass via gunicorn."""
    # Project
    from hyperglass.api import app

    HyperglassWSGI(
        app=app,
        options={
            "worker_class": "uvicorn.workers.UvicornWorker",
            "preload": True,
            "keepalive": 10,
            "command": shutil.which("gunicorn"),
            "bind": ":".join(
                (format_listen_address(params.listen_address), str(params.listen_port))
            ),
            "workers": workers,
            "loglevel": loglevel,
            "timeout": math.ceil(params.request_timeout * 1.25),
            "on_starting": on_starting,
            "on_exit": on_exit,
            "logger_class": StubbedGunicornLogger,
            "accesslog": "-",
            "errorlog": "-",
            "logconfig_dict": {"formatters": {"generic": {"format": "%(message)s"}}},
            **kwargs,
        },
    ).run()


if __name__ == "__main__":
    start()
