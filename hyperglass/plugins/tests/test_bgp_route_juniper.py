"""Juniper BGP Route Parsing Tests."""

# flake8: noqa
# Standard Library
from pathlib import Path

# Third Party
import pytest

# Project
from hyperglass.models.data.bgp_route import BGPRouteTable

# Local
from ._fixtures import MockDevice
from .._builtin.bgp_route_juniper import BGPRoutePluginJuniper

DEPENDS_KWARGS = {
    "depends": [
        "hyperglass/models/tests/test_util.py::test_check_legacy_fields",
        "hyperglass/external/tests/test_rpki.py::test_rpki",
    ],
    "scope": "session",
}

DIRECT = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_direct.xml"
INDIRECT = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_indirect.xml"
AS_PATH = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_aspath.xml"


def _tester(sample: str):
    plugin = BGPRoutePluginJuniper()

    device = MockDevice(
        name="Test Device",
        address="127.0.0.1",
        group="Test Network",
        credential={"username": "", "password": ""},
        platform="juniper",
        structured_output=True,
        directives=[],
        attrs={"source4": "192.0.2.1", "source6": "2001:db8::1"},
    )

    query = type("Query", (), {"device": device})

    result = plugin.process(output=(sample,), query=query)
    assert isinstance(result, BGPRouteTable), "Invalid parsed result"
    assert hasattr(result, "count"), "BGP Table missing count"
    assert result.count > 0, "BGP Table count is 0"


@pytest.mark.dependency(**DEPENDS_KWARGS)
def test_juniper_bgp_route_direct():
    with DIRECT.open("r") as file:
        sample = file.read()
    return _tester(sample)


@pytest.mark.dependency(**DEPENDS_KWARGS)
def test_juniper_bgp_route_indirect():
    with INDIRECT.open("r") as file:
        sample = file.read()
    return _tester(sample)


@pytest.mark.dependency(**DEPENDS_KWARGS)
def test_juniper_bgp_route_aspath():
    with AS_PATH.open("r") as file:
        sample = file.read()
    return _tester(sample)
