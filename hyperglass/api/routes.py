"""API Routes."""

# Standard Library
import time
import typing as t
from datetime import datetime

# Third Party
from fastapi import Depends, HTTPException, BackgroundTasks
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.log import log
from hyperglass.state import HyperglassState, use_state
from hyperglass.constants import __version__
from hyperglass.models.ui import UIParameters
from hyperglass.exceptions import HyperglassError
from hyperglass.models.api import Query
from hyperglass.models.data import OutputDataModel
from hyperglass.util.typing import is_type
from hyperglass.execution.main import execute
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices

# Local
from .tasks import send_webhook
from .fake_output import fake_output


def get_state(attr: t.Optional[str] = None):
    """Get hyperglass state as a FastAPI dependency."""
    return use_state(attr)


def get_params():
    """Get hyperglass params as FastAPI dependency."""
    return use_state("params")


def get_devices():
    """Get hyperglass devices as FastAPI dependency."""
    return use_state("devices")


def get_ui_params():
    """Get hyperglass ui_params as FastAPI dependency."""
    return use_state("ui_params")


async def query(
    query_data: Query,
    request: Request,
    background_tasks: BackgroundTasks,
    state: "HyperglassState" = Depends(get_state),
):
    """Ingest request data pass it to the backend application to perform the query."""

    timestamp = datetime.utcnow()
    background_tasks.add_task(send_webhook, query_data, request, timestamp)

    # Initialize cache
    cache = state.redis

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = f"hyperglass.query.{query_data.digest()}"

    log.info("{!r} starting query execution", query_data)

    cache_response = cache.get_map(cache_key, "output")
    json_output = False
    cached = False
    runtime = 65535

    if cache_response:
        log.debug("{!r} cache hit (cache key {!r})", query_data, cache_key)

        # If a cached response exists, reset the expiration time.
        cache.expire(cache_key, expire_in=state.params.cache.timeout)

        cached = True
        runtime = 0
        timestamp = cache.get_map(cache_key, "timestamp")

    elif not cache_response:
        log.debug("{!r} cache miss (cache key {!r})", query_data, cache_key)

        timestamp = query_data.timestamp

        starttime = time.time()

        if state.params.fake_output:
            # Return fake, static data for development purposes, if enabled.
            output = await fake_output(query_data.device.structured_output or False)
        else:
            # Pass request to execution module
            output = await execute(query_data)

        endtime = time.time()
        elapsedtime = round(endtime - starttime, 4)
        log.debug("{!r} runtime: {!s} seconds", query_data, elapsedtime)

        if output is None:
            raise HyperglassError(message=state.params.messages.general, alert="danger")

        json_output = is_type(output, OutputDataModel)

        if json_output:
            raw_output = output.export_dict()
        else:
            raw_output = str(output)

        cache.set_map_item(cache_key, "output", raw_output)
        cache.set_map_item(cache_key, "timestamp", timestamp)
        cache.expire(cache_key, expire_in=state.params.cache.timeout)

        log.debug("{!r} cached for {!s} seconds", query_data, state.params.cache.timeout)

        runtime = int(round(elapsedtime, 0))

    # If it does, return the cached entry
    cache_response = cache.get_map(cache_key, "output")

    json_output = is_type(cache_response, t.Dict)
    response_format = "text/plain"

    if json_output:
        response_format = "application/json"

    log.success("{!r} execution completed", query_data)

    return {
        "output": cache_response,
        "id": cache_key,
        "cached": cached,
        "runtime": runtime,
        "timestamp": timestamp,
        "format": response_format,
        "random": query_data.random(),
        "level": "success",
        "keywords": [],
    }


async def docs(params: "Params" = Depends(get_params)):
    """Serve custom docs."""
    if params.docs.enable:
        docs_func_map = {"swagger": get_swagger_ui_html, "redoc": get_redoc_html}
        docs_func = docs_func_map[params.docs.mode]
        return docs_func(
            openapi_url=params.docs.openapi_url, title=params.site_title + " - API Docs"
        )
    else:
        raise HTTPException(detail="Not found", status_code=404)


async def router(id: str, devices: "Devices" = Depends(get_devices)):
    """Get a device's API-facing attributes."""
    return devices[id].export_api()


async def routers(devices: "Devices" = Depends(get_devices)):
    """Serve list of configured routers and attributes."""
    return devices.export_api()


async def queries(params: "Params" = Depends(get_params)):
    """Serve list of enabled query types."""
    return params.queries.list


async def info(params: "Params" = Depends(get_params)):
    """Serve general information about this instance of hyperglass."""
    return {
        "name": params.site_title,
        "organization": params.org_name,
        "primary_asn": int(params.primary_asn),
        "version": __version__,
    }


async def ui_props(ui_params: "UIParameters" = Depends(get_ui_params)):
    """Serve UI configration."""
    return ui_params


endpoints = [query, docs, routers, info, ui_props]
