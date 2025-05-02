"""Test external http client."""
# Standard Library
import asyncio

# Third Party
import pytest

# Project
from hyperglass.exceptions.private import ExternalError
from hyperglass.models.config.logging import Http

# Local
from .._base import BaseExternal

config = Http(provider="generic", host="https://httpbin.org")


def test_base_external_sync():
    with BaseExternal(base_url="https://httpbin.org", config=config) as client:
        res1 = client._get("/get")
        res2 = client._get("/get", params={"key": "value"})
        res3 = client._post("/post", data={"strkey": "value", "intkey": 1})
    assert res1["url"] == "https://httpbin.org/get"
    assert res2["args"].get("key") == "value"
    assert res3["json"].get("strkey") == "value"
    assert res3["json"].get("intkey") == 1

    with pytest.raises(ExternalError):
        with BaseExternal(base_url="https://httpbin.org", config=config, timeout=2) as client:
            client._get("/delay/4")


async def _run_test_base_external_async():
    async with BaseExternal(base_url="https://httpbin.org", config=config) as client:
        res1 = await client._aget("/get")
        res2 = await client._aget("/get", params={"key": "value"})
        res3 = await client._apost("/post", data={"strkey": "value", "intkey": 1})
    assert res1["url"] == "https://httpbin.org/get"
    assert res2["args"].get("key") == "value"
    assert res3["json"].get("strkey") == "value"
    assert res3["json"].get("intkey") == 1

    with pytest.raises(ExternalError):
        async with BaseExternal(base_url="https://httpbin.org", config=config, timeout=2) as client:
            await client._get("/delay/4")


def test_base_external_async():
    asyncio.run(_run_test_base_external_async())
