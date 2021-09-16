"""Gunicorn Config File."""

# Standard Library
import sys
import shutil
import typing as t
import asyncio
import platform

# Third Party
from gunicorn.arbiter import Arbiter  # type: ignore
from gunicorn.app.base import BaseApplication  # type: ignore

# Local
from .log import GunicornLogger, log, set_log_level, setup_lib_logging
from .plugins import (
    InputPluginManager,
    OutputPluginManager,
    register_plugin,
    init_builtin_plugins,
)
from .constants import MIN_NODE_VERSION, MIN_PYTHON_VERSION, __version__
from .util.frontend import get_node_version

if t.TYPE_CHECKING:
    # Local
    from .models.config.devices import Devices

# Ensure the Python version meets the minimum requirements.
pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
if sys.version_info < MIN_PYTHON_VERSION:
    raise RuntimeError(f"Python {pretty_version}+ is required.")

# Ensure the NodeJS version meets the minimum requirements.
node_major, _, __ = get_node_version()

if node_major != MIN_NODE_VERSION:
    raise RuntimeError(f"NodeJS {MIN_NODE_VERSION!s}+ is required.")


# Local
from .util import cpu_count
from .state import use_state
from .settings import Settings
from .util.frontend import build_frontend


async def build_ui() -> bool:
    """Perform a UI build prior to starting the application."""
    state = use_state()
    await build_frontend(
        dev_mode=Settings.dev_mode,
        dev_url=Settings.dev_url,
        prod_url=Settings.prod_url,
        params=state.ui_params,
        app_path=Settings.app_path,
    )
    return True


def register_all_plugins(devices: "Devices") -> None:
    """Validate and register configured plugins."""

    # Register built-in plugins.
    init_builtin_plugins()

    # Register external plugins.
    for plugin_file, directives in devices.directive_plugins().items():
        failures = register_plugin(plugin_file, directives=directives)
        for failure in failures:
            log.warning(
                "Plugin '{}' is not a valid hyperglass plugin, and was not registered", failure,
            )


def unregister_all_plugins() -> None:
    """Unregister all plugins."""
    for manager in (InputPluginManager, OutputPluginManager):
        manager().reset()


def on_starting(server: "Arbiter"):
    """Gunicorn pre-start tasks."""

    python_version = platform.python_version()
    required = ".".join((str(v) for v in MIN_PYTHON_VERSION))
    log.debug("Python {} detected ({} required)", python_version, required)

    state = use_state()

    register_all_plugins(state.devices)

    asyncio.run(build_ui())

    log.success(
        "Started hyperglass {} on http://{} with {!s} workers",
        __version__,
        Settings.bind(),
        server.app.cfg.settings["workers"].value,
    )


def on_exit(server: "Arbiter"):
    """Gunicorn shutdown tasks."""

    log.critical("Stopping hyperglass {}", __version__)

    state = use_state()
    if not Settings.dev_mode:
        state.clear()

    unregister_all_plugins()


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

    set_log_level(log, Settings.debug)

    log.debug("System settings: {!r}", Settings)

    workers, log_level = 1, "DEBUG"
    if Settings.debug is False:
        workers, log_level = cpu_count(2), "WARNING"

    setup_lib_logging(log_level)

    HyperglassWSGI(
        app="hyperglass.api:app",
        options={
            "preload": True,
            "errorlog": "-",
            "accesslog": "-",
            "workers": workers,
            "on_exit": on_exit,
            "loglevel": log_level,
            "bind": Settings.bind(),
            "on_starting": on_starting,
            "command": shutil.which("gunicorn"),
            "logger_class": GunicornLogger,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "logconfig_dict": {"formatters": {"generic": {"format": "%(message)s"}}},
            **kwargs,
        },
    ).run()


if __name__ == "__main__":
    try:
        start()
    except Exception as error:
        # Handle app exceptions.
        if not Settings.dev_mode:
            state = use_state()
            state.clear()
            log.info("Cleared Redis cache")
        unregister_all_plugins()
        raise error
    except SystemExit:
        # Handle Gunicorn exit.
        sys.exit(4)
