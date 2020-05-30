"""API Routes."""

# Standard Library
import os
import json
import time

# Third Party
from fastapi import HTTPException
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.log import log
from hyperglass.util import clean_name, process_headers, import_public_key
from hyperglass.cache import Cache
from hyperglass.encode import jwt_decode
from hyperglass.external import Webhook, RIPEStat
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import REDIS_CONFIG, params, devices
from hyperglass.api.models.query import Query
from hyperglass.execution.execute import Execute
from hyperglass.api.models.cert_import import EncodedRequest

APP_PATH = os.environ["hyperglass_directory"]


async def query(query_data: Query, request: Request):
    """Ingest request data pass it to the backend application to perform the query."""

    headers = await process_headers(headers=request.headers)

    async with RIPEStat() as ripe:
        network_info = await ripe.network_info(request.client.host, serialize=True)

    if params.logging.http is not None:
        async with Webhook(params.logging.http) as hook:
            await hook.send(
                query={
                    **query_data.export_dict(),
                    "headers": headers,
                    "source": request.client.host,
                    "network": network_info,
                }
            )

    # Initialize cache
    cache = Cache(db=params.cache.database, **REDIS_CONFIG)
    log.debug("Initialized cache {}", repr(cache))

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = query_data.digest()

    # Define cache entry expiry time
    cache_timeout = params.cache.timeout

    log.debug(f"Cache Timeout: {cache_timeout}")
    log.info(f"Starting query execution for query {query_data.summary}")

    cache_response = await cache.get_dict(cache_key, "output")

    cached = False
    if cache_response:
        log.debug("Query {q} exists in cache", q=cache_key)

        # If a cached response exists, reset the expiration time.
        await cache.expire(cache_key, seconds=cache_timeout)

        cached = True
        runtime = 0
        timestamp = await cache.get_dict(cache_key, "timestamp")

    elif not cache_response:
        log.debug(f"No existing cache entry for query {cache_key}")
        log.debug(
            f"Created new cache key {cache_key} entry for query {query_data.summary}"
        )

        timestamp = query_data.timestamp
        # Pass request to execution module
        starttime = time.time()
        cache_output = await Execute(query_data).response()
        endtime = time.time()
        elapsedtime = round(endtime - starttime, 4)
        log.debug(f"Query {cache_key} took {elapsedtime} seconds to run.")

        if cache_output is None:
            raise HyperglassError(message=params.messages.general, alert="danger")

        # Create a cache entry
        if query_data.device.structured_output:
            raw_output = json.dumps(cache_output)
        else:
            raw_output = str(cache_output)
        await cache.set_dict(cache_key, "output", raw_output)
        await cache.set_dict(cache_key, "timestamp", timestamp)
        await cache.expire(cache_key, seconds=cache_timeout)

        log.debug(f"Added cache entry for query: {cache_key}")

        runtime = int(round(elapsedtime, 0))

    # If it does, return the cached entry
    cache_response = await cache.get_dict(cache_key, "output")

    if query_data.device.structured_output:
        response_format = "application/json"
        cache_response = json.loads(cache_response)
    else:
        response_format = "text/plain"

    log.debug(f"Cache match for {cache_key}:\n {cache_response}")
    log.success(f"Completed query execution for {query_data.summary}")

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


async def import_certificate(encoded_request: EncodedRequest):
    """Import a certificate from hyperglass-agent."""

    # Try to match the requested device name with configured devices
    matched_device = None
    requested_device_name = clean_name(encoded_request.device)
    for device in devices.routers:
        if device.name == requested_device_name:
            matched_device = device
            break

    if matched_device is None:
        raise HTTPException(
            detail=f"Device {str(encoded_request.device)} not found", status_code=404
        )

    try:
        # Decode JSON Web Token
        decoded_request = await jwt_decode(
            payload=encoded_request.encoded,
            secret=matched_device.credential.password.get_secret_value(),
        )
    except HyperglassError as decode_error:
        raise HTTPException(detail=str(decode_error), status_code=401)

    try:
        # Write certificate to file
        import_public_key(
            app_path=APP_PATH, device_name=device.name, keystring=decoded_request
        )
    except RuntimeError as import_error:
        raise HyperglassError(str(import_error), level="danger")

    return {
        "output": f"Added public key for {encoded_request.device}",
        "level": "success",
        "keywords": [encoded_request.device],
    }


async def docs():
    """Serve custom docs."""
    if params.docs.enable:
        docs_func_map = {"swagger": get_swagger_ui_html, "redoc": get_redoc_html}
        docs_func = docs_func_map[params.docs.mode]
        return docs_func(
            openapi_url=params.docs.openapi_url, title=params.site_title + " - API Docs"
        )
    else:
        raise HTTPException(detail="Not found", status_code=404)


async def routers():
    """Serve list of configured routers and attributes."""
    return [
        d.dict(
            include={
                "name": ...,
                "network": ...,
                "location": ...,
                "display_name": ...,
                "vrfs": {-1: {"name", "display_name"}},
            }
        )
        for d in devices.routers
    ]


async def communities():
    """Serve list of configured communities if mode is select."""
    if params.queries.bgp_community.mode != "select":
        raise HTTPException(detail="BGP community mode is not select", status_code=404)

    return [c.export_dict() for c in params.queries.bgp_community.communities]


async def queries():
    """Serve list of enabled query types."""
    return params.queries.list


endpoints = [query, docs, routers]
