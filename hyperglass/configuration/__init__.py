"""hyperglass Configuration."""

# Project
from hyperglass.state import use_state
from hyperglass.defaults.directives import init_builtin_directives

# Local
from .validate import init_params, init_devices, init_ui_params, init_directives

__all__ = ("init_user_config",)


def init_user_config() -> None:
    """Initialize all user configurations and add them to global state."""
    state = use_state()

    params = init_params()
    builtins = init_builtin_directives()
    custom = init_directives()
    directives = builtins + custom
    with state.cache.pipeline() as pipeline:
        # Write params and directives to the cache first to avoid a race condition where ui_params
        # or devices try to access params or directives before they're available.
        pipeline.set("params", params)
        pipeline.set("directives", directives)

    devices = init_devices()
    ui_params = init_ui_params(params=params, devices=devices)
    with state.cache.pipeline() as pipeline:
        pipeline.set("devices", devices)
        pipeline.set("ui_params", ui_params)
