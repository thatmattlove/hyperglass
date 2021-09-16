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
    addr = "192.0.2.1"
    info = asyncio.run(network_info(addr))
    assert isinstance(info, dict)
    assert "192.0.2.1" in info, "Address missing"
    assert "asn" in info[addr], "ASN missing"
    assert info[addr]["asn"] == "0", "Unexpected ASN"
    assert info[addr]["rir"] == "Unknown", "Unexpected RIR"


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
