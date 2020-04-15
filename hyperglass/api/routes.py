"""API Routes."""

# Standard Library
import os
import json
import time
from ipaddress import ip_address

# Third Party
from fastapi import HTTPException
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.log import log, query_hook
from hyperglass.util import adonothing, clean_name, get_network_info, import_public_key
from hyperglass.cache import Cache
from hyperglass.encode import jwt_decode
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import REDIS_CONFIG, params, devices
from hyperglass.api.models.query import Query
from hyperglass.execution.execute import Execute
from hyperglass.api.models.cert_import import EncodedRequest

APP_PATH = os.environ["hyperglass_directory"]

if params.logging.http is not None and params.logging.http.enable:
    log_query = query_hook
else:
    log_query = adonothing


async def query(query_data: Query, request: Request):
    """Ingest request data pass it to the backend application to perform the query."""

    if ip_address(request.client.host).is_loopback:
        network_info = {"prefix": None, "asn": None}
    else:
        network_info = get_network_info("199.34.92.64")

        network_info = {
            "prefix": str(network_info["prefix"]),
            "asn": network_info["asns"][0],
        }

    header_keys = (
        "content-length",
        "accept",
        "user-agent",
        "content-type",
        "referer",
        "accept-encoding",
        "accept-language",
    )

    await log_query(
        {
            **json.loads(query_data.export_json()),
            "headers": {
                k: v for k, v in dict(request.headers).items() if k in header_keys
            },
            "source": request.client.host,
            "network": network_info,
        },
        params.logging.http,
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
    # Check if cached entry exists
    if not await cache.get(cache_key):
        log.debug(f"No existing cache entry for query {cache_key}")
        log.debug(
            f"Created new cache key {cache_key} entry for query {query_data.summary}"
        )

        # Pass request to execution module
        starttime = time.time()
        cache_value = await Execute(query_data).response()
        endtime = time.time()
        elapsedtime = round(endtime - starttime, 4)
        log.debug(f"Query {cache_key} took {elapsedtime} seconds to run.")

        if cache_value is None:
            raise HyperglassError(message=params.messages.general, alert="danger")

        # Create a cache entry
        await cache.set(cache_key, str(cache_value))
        await cache.expire(cache_key, seconds=cache_timeout)

        log.debug(f"Added cache entry for query: {cache_key}")

    # If it does, return the cached entry
    cache_response = await cache.get(cache_key)

    log.debug(f"Cache match for {cache_key}:\n {cache_response}")
    log.success(f"Completed query execution for {query_data.summary}")

    return {"output": cache_response, "level": "success", "keywords": []}


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


async def queries():
    """Serve list of enabled query types."""
    return params.queries.list


endpoints = [query, docs, routers]
