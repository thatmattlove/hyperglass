"""hyperglass Configuration."""

# Standard Library
import typing as t

# Project
from hyperglass.state import use_state
from hyperglass.defaults.directives import init_builtin_directives

# Local
from .validate import init_files, init_params, init_devices, init_ui_params, init_directives

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.directive import Directives
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices

__all__ = ("init_user_config",)


def init_user_config(
    params: t.Optional["Params"] = None,
    directives: t.Optional["Directives"] = None,
    devices: t.Optional["Devices"] = None,
) -> None:
    """Initialize all user configurations and add them to global state."""
    state = use_state()
    init_files()

    _params = params or init_params()
    builtins = init_builtin_directives()
    _custom = directives or init_directives()
    _directives = builtins + _custom
    with state.cache.pipeline() as pipeline:
        # Write params and directives to the cache first to avoid a race condition where ui_params
        # or devices try to access params or directives before they're available.
        pipeline.set("params", _params)
        pipeline.set("directives", _directives)

    _devices = devices or init_devices()
    ui_params = init_ui_params(params=_params, devices=_devices)
    with state.cache.pipeline() as pipeline:
        pipeline.set("devices", _devices)
        pipeline.set("ui_params", ui_params)
