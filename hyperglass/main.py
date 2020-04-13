"""Gunicorn Config File."""

# Standard Library
import sys
import math
import shutil
import platform

# Third Party
from gunicorn.arbiter import Arbiter
from gunicorn.app.base import BaseApplication

# Project
from hyperglass.constants import MIN_PYTHON_VERSION, __version__

pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
if sys.version_info < MIN_PYTHON_VERSION:
    raise RuntimeError(f"Python {pretty_version}+ is required.")


from hyperglass.configuration import (  # isort:skip
    params,
    URL_DEV,
    URL_PROD,
    CONFIG_PATH,
    REDIS_CONFIG,
    frontend_params,
)
from hyperglass.util import (  # isort:skip
    log,
    cpu_count,
    check_redis,
    build_frontend,
    clear_redis_cache,
    format_listen_address,
)
from hyperglass.compat._asyncio import aiorun  # isort:skip

if params.debug:
    workers = 1
    loglevel = "DEBUG"
else:
    workers = cpu_count(2)
    loglevel = "WARNING"


async def check_redis_instance():
    """Ensure Redis is running before starting server.

    Returns:
        {bool} -- True if Redis is running.
    """
    await check_redis(db=params.cache.database, config=REDIS_CONFIG)

    log.debug(f"Redis is running at: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    return True


async def build_ui():
    """Perform a UI build prior to starting the application.

    Returns:
        {bool} -- True if successful.
    """
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


def on_starting(server: Arbiter):
    """Gunicorn pre-start tasks."""

    python_version = platform.python_version()
    required = ".".join((str(v) for v in MIN_PYTHON_VERSION))
    log.info(f"Python {python_version} detected ({required} required)")

    aiorun(check_redis_instance())
    aiorun(build_ui())

    log.success(
        "Started hyperglass {v} on http://{h}:{p} with {w} workers",
        v=__version__,
        h=format_listen_address(params.listen_address),
        p=str(params.listen_port),
        w=server.app.cfg.settings["workers"].value,
    )


def on_exit(server: Arbiter):
    """Gunicorn shutdown tasks."""
    aiorun(clear_cache())
    log.critical("Stopped hyperglass {}", __version__)


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
            **kwargs,
        },
    ).run()


if __name__ == "__main__":
    start()
