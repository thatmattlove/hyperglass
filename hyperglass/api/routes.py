"""API Routes."""

# Standard Library
import os
import time

# Third Party
import aredis
from fastapi import HTTPException
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.util import log, clean_name, import_public_key
from hyperglass.encode import jwt_decode
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import REDIS_CONFIG, params, devices
from hyperglass.api.models.query import Query
from hyperglass.execution.execute import Execute
from hyperglass.api.models.cert_import import EncodedRequest

Cache = aredis.StrictRedis(db=params.cache.database, **REDIS_CONFIG)

APP_PATH = os.environ["hyperglass_directory"]


async def query(query_data: Query, request: Request):
    """Ingest request data pass it to the backend application to perform the query."""

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = query_data.digest()

    # Define cache entry expiry time
    cache_timeout = params.cache.timeout
    log.debug(f"Cache Timeout: {cache_timeout}")

    # Check if cached entry exists
    if not await Cache.get(cache_key):
        log.debug(f"Created new cache key {cache_key} entry for query {query_data}")
        log.debug("Beginning query execution...")

        # Pass request to execution module
        starttime = time.time()
        cache_value = await Execute(query_data).response()
        endtime = time.time()
        elapsedtime = round(endtime - starttime, 4)
        log.debug(f"Query {cache_key} took {elapsedtime} seconds to run.")

        if cache_value is None:
            raise HyperglassError(message=params.messages.general, alert="danger")

        # Create a cache entry
        await Cache.set(cache_key, str(cache_value))
        await Cache.expire(cache_key, cache_timeout)

        log.debug(f"Added cache entry for query: {cache_key}")

    # If it does, return the cached entry
    cache_response = await Cache.get(cache_key)

    log.debug(f"Cache match for: {cache_key}, returning cached entry")
    log.debug(f"Cache Output: {cache_response}")

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
