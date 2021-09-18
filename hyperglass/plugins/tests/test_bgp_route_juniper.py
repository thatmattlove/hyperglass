"""Juniper BGP Route Parsing Tests."""

# flake8: noqa
# Standard Library
from pathlib import Path

# Third Party
import pytest

# Project
from hyperglass.log import log
from hyperglass.models.config.devices import Device
from hyperglass.models.data.bgp_route import BGPRouteTable

# Local
from .._builtin.bgp_route_juniper import BGPRoutePluginJuniper

DEPENDS_KWARGS = {
    "depends": ["hyperglass/external/tests/test_rpki.py::test_rpki"],
    "scope": "session",
}

DIRECT = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_direct.xml"
INDIRECT = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_indirect.xml"
AS_PATH = Path(__file__).parent.parent.parent.parent / ".samples" / "juniper_route_aspath.xml"


def _tester(sample: str):
    plugin = BGPRoutePluginJuniper()

    device = Device(
        name="Test Device",
        address="127.0.0.1",
        network={"name": "Test Network", "display_name": "Test Network"},
        credential={"username": "", "password": ""},
        platform="juniper",
        structured_output=True,
        directives=[],
        attrs={"source4": "192.0.2.1", "source6": "2001:db8::1"},
    )

    # Override has_directives method for testing.
    device.has_directives = lambda *x: True

    result = plugin.process((sample,), device)
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
