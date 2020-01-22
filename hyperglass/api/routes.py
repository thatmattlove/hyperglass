"""API Routes."""

# Standard Library Imports
import time

# Third Party Imports
import aredis
from fastapi import HTTPException
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.requests import Request

# Project Imports
from hyperglass.configuration import REDIS_CONFIG
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.execution.execute import Execute
from hyperglass.models.query import Query
from hyperglass.util import log

Cache = aredis.StrictRedis(db=params.features.cache.redis_id, **REDIS_CONFIG)


async def query(query_data: Query, request: Request):
    """Ingest request data pass it to the backend application to perform the query."""

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = hash(str(query_data))

    # Define cache entry expiry time
    cache_timeout = params.features.cache.timeout
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
    if params.general.docs.enable:
        docs_func_map = {"swagger": get_swagger_ui_html, "redoc": get_redoc_html}
        docs_func = docs_func_map[params.general.docs.mode]
        return docs_func(
            openapi_url=params.general.docs.openapi_url,
            title=params.general.site_title + " - API Docs",
        )
    else:
        raise HTTPException(detail="Not found", status_code=404)


endpoints = [query, docs]
