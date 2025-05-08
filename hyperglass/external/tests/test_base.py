"""Test external http client."""

# Standard Library
import asyncio
import os

# Third Party
import pytest

# Project
from hyperglass.exceptions.private import ExternalError
from hyperglass.models.config.logging import Http

# Local
from .._base import BaseExternal


@pytest.fixture
def httpbin_url():
    # get HYPERGLASS_TEST_HTTPBIN
    httpbin_host: str = os.environ.get("HYPERGLASS_HTTPBIN_HOST", "httpbin.org")
    httpbin_port: int = os.environ.get("HYPERGLASS_HTTPBIN_PORT", 443)
    httpbin_protocol: str = os.environ.get("HYPERGLASS_HTTPBIN_PROTOCOL", "https")

    url = f"{httpbin_protocol}://{httpbin_host}"
    if httpbin_port != 443 and httpbin_port != 80:
        url = f"{url}:{httpbin_port}"
    return url


@pytest.fixture
def httpbin_config(httpbin_url):
    return Http(provider="generic", host=httpbin_url)


def test_base_external_sync(httpbin_url, httpbin_config):
    with BaseExternal(base_url=httpbin_url, config=httpbin_config) as client:
        res1 = client._get("/get")
        res2 = client._get("/get", params={"key": "value"})
        res3 = client._post("/post", data={"strkey": "value", "intkey": 1})
    assert res1["url"] == f"{httpbin_url}/get"
    assert res2["args"].get("key") == "value"
    assert res3["json"].get("strkey") == "value"
    assert res3["json"].get("intkey") == 1

    with pytest.raises(ExternalError):
        with BaseExternal(base_url=httpbin_url, config=httpbin_config, timeout=2) as client:
            client._get("/delay/4")


async def _run_test_base_external_async(httpbin_url, httpbin_config):
    async with BaseExternal(base_url=httpbin_url, config=httpbin_config) as client:
        res1 = await client._aget("/get")
        res2 = await client._aget("/get", params={"key": "value"})
        res3 = await client._apost("/post", data={"strkey": "value", "intkey": 1})
    assert res1["url"] == f"{httpbin_url}/get"
    assert res2["args"].get("key") == "value"
    assert res3["json"].get("strkey") == "value"
    assert res3["json"].get("intkey") == 1

    with pytest.raises(ExternalError):
        async with BaseExternal(base_url=httpbin_url, config=httpbin_config, timeout=2) as client:
            await client._get("/delay/4")


def test_base_external_async(httpbin_url, httpbin_config):
    asyncio.run(_run_test_base_external_async(httpbin_url, httpbin_config))
