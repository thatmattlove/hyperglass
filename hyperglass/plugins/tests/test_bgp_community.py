"""Test BGP Community validation."""

# Local
from .._builtin.bgp_community import ValidateBGPCommunity

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


def test_bgp_community():
    plugin = ValidateBGPCommunity()

    for value, expected in CHECKS:
        query = type("Query", (), {"query_target": value})
        result = plugin.validate(query)
        assert result == expected, f"Invalid value {value!r}"
