"""Test BGP Community validation."""
# Standard Library
import typing as t

# Third Party
import pytest

# Project
from hyperglass.state import use_state
from hyperglass.models.config.params import Params

# Local
from .._builtin.bgp_community import ValidateBGPCommunity

if t.TYPE_CHECKING:
    # Project
    from hyperglass.state import HyperglassState


CHECKS = (
    ("32768", True),
    ("65000:1", True),
    ("65000:4294967296", False),
    ("4294967295:65000", False),
    ("192.0.2.1:65000", True),
    ("65000:192.0.2.1", False),
    ("target:65000:1", True),
    ("origin:65001:1", True),
    ("wrong:65000:1", False),
    ("65000:65001:65002", True),
    ("4294967295:4294967294:4294967293", True),
    ("65000:4294967295:1", True),
    ("65000:192.0.2.1:1", False),
    ("gibberish", False),
    ("192.0.2.1", False),
    (True, None),
    (type("FakeClass", (), {}), None),
)


@pytest.fixture
def params():
    return {}


@pytest.fixture
def state(*, params: t.Dict[str, t.Any]) -> t.Generator["HyperglassState", None, None]:
    """Test fixture to initialize Redis store."""
    _state = use_state()
    _params = Params(**params)

    with _state.cache.pipeline() as pipeline:
        pipeline.set("params", _params)

    yield _state
    _state.clear()


def test_bgp_community(state):
    plugin = ValidateBGPCommunity()

    for value, expected in CHECKS:
        query = type("Query", (), {"query_target": value})
        result = plugin.validate(query)
        assert result == expected, f"Invalid value {value!r}"
