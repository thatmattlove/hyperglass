"""Test bgp.tools interactions."""

# Standard Library
import asyncio

# Third Party
import pytest

# Local
from ..bgptools import run_whois, parse_whois, network_info

WHOIS_OUTPUT = """AS    | IP      | BGP Prefix | CC | Registry | Allocated  | AS Name
13335 | 1.1.1.1 | 1.1.1.0/24 | US | ARIN     | 2010-07-14 | Cloudflare, Inc."""


# Ignore asyncio deprecation warning about loop
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_network_info():

    checks = (
        ("192.0.2.1", {"asn": "None", "rir": "Private Address"}),
        ("127.0.0.1", {"asn": "None", "rir": "Loopback Address"}),
        ("fe80:dead:beef::1", {"asn": "None", "rir": "Link Local Address"}),
        ("2001:db8::1", {"asn": "None", "rir": "Private Address"}),
        ("1.1.1.1", {"asn": "13335", "rir": "ARIN"}),
    )
    for addr, fields in checks:
        info = asyncio.run(network_info(addr))
        assert addr in info
        for key, expected in fields.items():
            assert info[addr][key] == expected


# Ignore asyncio deprecation warning about loop
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_whois():
    addr = "192.0.2.1"
    response = asyncio.run(run_whois([addr]))
    assert isinstance(response, str)
    assert response != ""


def test_whois_parser():
    addr = "1.1.1.1"
    result = parse_whois(WHOIS_OUTPUT, [addr])
    assert isinstance(result, dict)
    assert addr in result, "Address missing"
    assert result[addr]["asn"] == "13335"
    assert result[addr]["rir"] == "ARIN"
    assert result[addr]["org"] == "Cloudflare, Inc."
