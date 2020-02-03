"""API Routes."""

# Standard Library
import time

# Third Party
import aredis
from fastapi import HTTPException
from starlette.requests import Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Project
from hyperglass.util import log
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import REDIS_CONFIG, params, devices
from hyperglass.api.models.query import Query
from hyperglass.execution.execute import Execute

Cache = aredis.StrictRedis(db=params.cache.database, **REDIS_CONFIG)


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
