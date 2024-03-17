"""Arista BGP Route Parsing Tests."""

# flake8: noqa
# Standard Library
from pathlib import Path

# Third Party
import pytest

# Project
from hyperglass.models.config.devices import Device
from hyperglass.models.data.bgp_route import BGPRouteTable

# Local
from ._fixtures import MockDevice
from .._builtin.bgp_route_arista import BGPRoutePluginArista

DEPENDS_KWARGS = {
    "depends": [
        "hyperglass/models/tests/test_util.py::test_check_legacy_fields",
        "hyperglass/external/tests/test_rpki.py::test_rpki",
    ],
    "scope": "session",
}

SAMPLE = Path(__file__).parent.parent.parent.parent / ".samples" / "arista_route.json"


def _tester(sample: str):
    plugin = BGPRoutePluginArista()

    device = MockDevice(
        name="Test Device",
        address="127.0.0.1",
        group="Test Network",
        credential={"username": "", "password": ""},
        platform="arista",
        structured_output=True,
        directives=["__hyperglass_arista_eos_bgp_route_table__"],
        attrs={"source4": "192.0.2.1", "source6": "2001:db8::1"},
    )

    query = type("Query", (), {"device": device})

    result = plugin.process(output=(sample,), query=query)
    assert isinstance(result, BGPRouteTable), "Invalid parsed result"
    assert hasattr(result, "count"), "BGP Table missing count"
    assert result.count > 0, "BGP Table count is 0"


@pytest.mark.dependency(**DEPENDS_KWARGS)
def test_arista_route_sample():
    with SAMPLE.open("r") as file:
        sample = file.read()
    return _tester(sample)
