"""Test state hooks."""

# Standard Library
import typing as t

# Third Party
import pytest

if t.TYPE_CHECKING:
    from hyperglass.state import HyperglassState

# Project
from hyperglass.models.ui import UIParameters
from hyperglass.configuration import init_ui_params
from hyperglass.models.directive import Directives
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices

# Local
from ..hooks import use_state
from ..store import HyperglassState

STATE_ATTRS = (
    ("params", Params),
    ("devices", Devices),
    ("ui_params", UIParameters),
    ("directives", Directives),
    (None, HyperglassState),
)


@pytest.fixture
def params():
    return {}


@pytest.fixture
def devices():
    return [
        {
            "name": "test1",
            "address": "127.0.0.1",
            "credential": {"username": "", "password": ""},
            "platform": "juniper",
            "attrs": {"source4": "192.0.2.1", "source6": "2001:db8::1"},
            "directives": ["juniper_bgp_route"],
        }
    ]


@pytest.fixture
def directives():
    return [
        {
            "juniper_bgp_route": {
                "name": "BGP Route",
                "field": {"description": "test"},
            }
        }
    ]


@pytest.fixture
def state(
    *,
    params: t.Dict[str, t.Any],
    directives: t.Sequence[t.Dict[str, t.Any]],
    devices: t.Sequence[t.Dict[str, t.Any]],
) -> t.Generator["HyperglassState", None, None]:
    """Test fixture to initialize Redis store."""
    _state = use_state()
    _params = Params(**params)
    _directives = Directives.new(*directives)

    with _state.cache.pipeline() as pipeline:
        # Write params and directives to the cache first to avoid a race condition where ui_params
        # or devices try to access params or directives before they're available.
        pipeline.set("params", _params)
        pipeline.set("directives", _directives)

    _devices = Devices(*devices)
    ui_params = init_ui_params(params=_params, devices=_devices)

    with _state.cache.pipeline() as pipeline:
        pipeline.set("devices", _devices)
        pipeline.set("ui_params", ui_params)

    yield _state
    _state.clear()


def test_use_state_caching(state):
    first = None
    for attr, model in STATE_ATTRS:
        for i in range(0, 5):
            instance = use_state(attr)
            if i == 0:
                first = instance
            assert isinstance(
                instance, model
            ), f"{instance!r} is not an instance of '{model.__name__}'"
            assert instance == first, f"{instance!r} is not equal to {first!r}"
