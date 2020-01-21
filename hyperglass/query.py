"""Hyperglass Front End."""

# Standard Library Imports
import time

# Third Party Imports
import aredis

# Project Imports
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.execution.execute import Execute
from hyperglass.util import log

log.debug(f"Configuration Parameters: {params.dict(by_alias=True)}")

# Redis Config
REDIS_CONFIG = {
    "host": str(params.general.redis_host),
    "port": params.general.redis_port,
    "decode_responses": True,
}

Cache = aredis.StrictRedis(db=params.features.cache.redis_id, **REDIS_CONFIG)


async def handle_query(query_data):
    """Process XHR POST data.

    Ingests XHR POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """

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

    return cache_response
