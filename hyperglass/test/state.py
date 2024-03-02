"""State-related test helpers."""

import typing as t

from hyperglass.state import use_state
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices
from hyperglass.models.directive import Directives
from hyperglass.configuration import init_ui_params


def initialize_state(
    *,
    params: t.Dict[str, t.Any],
    directives: t.Sequence[t.Dict[str, t.Any]],
    devices: t.Sequence[t.Dict[str, t.Any]],
) -> None:
    """Test fixture to initialize Redis store."""
    state = use_state()
    _params = Params(**params)
    _directives = Directives.new(*directives)

    with state.cache.pipeline() as pipeline:
        # Write params and directives to the cache first to avoid a race condition where ui_params
        # or devices try to access params or directives before they're available.
        pipeline.set("params", _params)
        pipeline.set("directives", _directives)

    # _devices = Devices.new(*devices)
    _devices = Devices(*devices)
    ui_params = init_ui_params(params=_params, devices=_devices)

    with state.cache.pipeline() as pipeline:
        pipeline.set("devices", _devices)
        pipeline.set("ui_params", ui_params)
