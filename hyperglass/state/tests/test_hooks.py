"""Test state hooks."""

# Project
from hyperglass.models.ui import UIParameters
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices

# Local
from ..hooks import use_state
from ..store import HyperglassState

STATE_ATTRS = (
    ("params", Params),
    ("devices", Devices),
    ("ui_params", UIParameters),
    (None, HyperglassState),
)


def test_use_state_caching():
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
