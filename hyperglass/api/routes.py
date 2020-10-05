"""API Routes."""

# Standard Library
import os
import json
import time
from datetime import datetime

# Third Party
from fastapi import HTTPException, BackgroundTasks
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.log import log
from hyperglass.cache import AsyncCache
from hyperglass.encode import jwt_decode
from hyperglass.external import Webhook, bgptools
from hyperglass.api.tasks import process_headers, import_public_key
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError
from hyperglass.models.api import Query, EncodedRequest
from hyperglass.configuration import REDIS_CONFIG, params, devices
from hyperglass.execution.main import execute

APP_PATH = os.environ["hyperglass_directory"]


async def send_webhook(query_data: Query, request: Request, timestamp: datetime):
    """If webhooks are enabled, get request info and send a webhook.

    Args:
        query_data (Query): Valid query
        request (Request): Starlette/FastAPI request

    Returns:
        int: Returns 1 regardless of result
    """
    try:
        if params.logging.http is not None:
            headers = await process_headers(headers=request.headers)

            if headers.get("x-real-ip") is not None:
                host = headers["x-real-ip"]
            elif headers.get("x-forwarded-for") is not None:
                host = headers["x-forwarded-for"]
            else:
                host = request.client.host

            network_info = await bgptools.network_info(host)

            async with Webhook(params.logging.http) as hook:

                await hook.send(
                    query={
                        **query_data.export_dict(pretty=True),
                        "headers": headers,
                        "source": host,
                        "network": network_info.get(host, {}),
                        "timestamp": timestamp,
                    }
                )
    except Exception as err:
        log.error(
            "Error sending webhook to {}: {}", params.logging.http.provider, str(err)
        )


async def query(query_data: Query, request: Request, background_tasks: BackgroundTasks):
    """Ingest request data pass it to the backend application to perform the query."""

    timestamp = datetime.utcnow()
    background_tasks.add_task(send_webhook, query_data, request, timestamp)

    # Initialize cache
    cache = AsyncCache(db=params.cache.database, **REDIS_CONFIG)
    log.debug("Initialized cache {}", repr(cache))

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = query_data.digest()

    # Define cache entry expiry time
    cache_timeout = params.cache.timeout

    log.debug("Cache Timeout: {}", cache_timeout)
    log.info("Starting query execution for query {}", query_data.summary)

    cache_response = await cache.get_dict(cache_key, "output")

    json_output = False

    if query_data.device.structured_output and query_data.query_type in (
        "bgp_route",
        "bgp_community",
        "bgp_aspath",
    ):
        json_output = True

    cached = False
    if cache_response:
        log.debug("Query {} exists in cache", cache_key)

        # If a cached response exists, reset the expiration time.
        await cache.expire(cache_key, seconds=cache_timeout)

        cached = True
        runtime = 0
        timestamp = await cache.get_dict(cache_key, "timestamp")

    elif not cache_response:
        log.debug("No existing cache entry for query {}", cache_key)
        log.debug(
            "Created new cache key {} entry for query {}", cache_key, query_data.summary
        )

        timestamp = query_data.timestamp
        # Pass request to execution module
        starttime = time.time()
        cache_output = await execute(query_data)
        endtime = time.time()
        elapsedtime = round(endtime - starttime, 4)
        log.debug("Query {} took {} seconds to run.", cache_key, elapsedtime)

        if cache_output is None:
            raise HyperglassError(message=params.messages.general, alert="danger")

        # Create a cache entry
        if json_output:
            raw_output = json.dumps(cache_output)
        else:
            raw_output = str(cache_output)
        await cache.set_dict(cache_key, "output", raw_output)
        await cache.set_dict(cache_key, "timestamp", timestamp)
        await cache.expire(cache_key, seconds=cache_timeout)

        log.debug("Added cache entry for query: {}", cache_key)

        runtime = int(round(elapsedtime, 0))

    # If it does, return the cached entry
    cache_response = await cache.get_dict(cache_key, "output")
    response_format = "text/plain"

    if json_output:
        response_format = "application/json"

    log.debug("Cache match for {}:\n{}", cache_key, cache_response)
    log.success("Completed query execution for query {}", query_data.summary)

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
    try:
        matched_device = devices[encoded_request.device]
    except AttributeError:
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
        raise HTTPException(detail=str(decode_error), status_code=400)

    try:
        # Write certificate to file
        import_public_key(
            app_path=APP_PATH,
            device_name=matched_device.name,
            keystring=decoded_request,
        )
    except RuntimeError as err:
        raise HyperglassError(str(err), level="danger")

    log.info("Added public key for {}", encoded_request.device)
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
                "display_name": ...,
                "vrfs": {-1: {"name", "display_name"}},
            }
        )
        for d in devices.objects
    ]


async def communities():
    """Serve list of configured communities if mode is select."""
    if params.queries.bgp_community.mode != "select":
        raise HTTPException(detail="BGP community mode is not select", status_code=404)

    return [c.export_dict() for c in params.queries.bgp_community.communities]


async def queries():
    """Serve list of enabled query types."""
    return params.queries.list


async def info():
    """Serve general information about this instance of hyperglass."""
    return {
        "name": params.site_title,
        "organization": params.org_name,
        "primary_asn": int(params.primary_asn),
        "version": f"hyperglass {__version__}",
    }


endpoints = [query, docs, routers, info]
