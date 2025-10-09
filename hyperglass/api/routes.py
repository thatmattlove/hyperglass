"""API Routes."""

# Standard Library
import asyncio
import json
import time
import typing as t
from datetime import UTC, datetime
from functools import partial

# Third Party
from litestar import Request, Response, get, post
from litestar.di import Provide
from litestar.background_tasks import BackgroundTask

# Project
from hyperglass.log import log
from hyperglass.state import HyperglassState
from hyperglass.exceptions import HyperglassError
from hyperglass.exceptions.public import DeviceTimeout, ResponseEmpty
from hyperglass.models.api import Query
from hyperglass.models.data import OutputDataModel
from hyperglass.util.typing import is_type
from hyperglass.execution.main import execute
from hyperglass.models.api.response import QueryResponse
from hyperglass.models.config.params import Params, APIParams
from hyperglass.models.config.devices import Devices, APIDevice

# Local
from .state import get_state, get_params, get_devices
from .tasks import send_webhook
from .fake_output import fake_output

# Global query deduplication tracking
_ongoing_queries: t.Dict[str, asyncio.Event] = {}


async def _cleanup_query_event(cache_key: str) -> None:
    """Clean up completed query event after a short delay."""
    await asyncio.sleep(5)  # Allow time for waiting requests to proceed
    _ongoing_queries.pop(cache_key, None)


# Global dict to track ongoing queries to prevent duplicate execution
_ongoing_queries: t.Dict[str, asyncio.Event] = {}


async def _cleanup_query_event(cache_key: str) -> None:
    """Clean up completed query event after a short delay."""
    await asyncio.sleep(1)  # Allow waiting requests to proceed
    _ongoing_queries.pop(cache_key, None)


__all__ = (
    "device",
    "devices",
    "queries",
    "info",
    "query",
)


@post("/api/aspath/enrich")
async def aspath_enrich(data: dict) -> dict:
    """Enrich a list of ASNs with organization names on demand.

    Expected JSON payload: { "as_path": [123, 456, ...] }
    """
    try:
        as_path = data.get("as_path", []) if isinstance(data, dict) else []
        if not as_path:
            return {"success": False, "error": "No as_path provided"}

        # Convert to strings and call the existing bulk lookup
        from hyperglass.external.ip_enrichment import lookup_asns_bulk

        asn_strings = [str(a) for a in as_path]
        results = await lookup_asns_bulk(asn_strings)
        return {"success": True, "asn_organizations": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


@get("/api/devices/{id:str}", dependencies={"devices": Provide(get_devices)})
async def device(devices: Devices, id: str) -> APIDevice:
    """Retrieve a device by ID."""
    return devices[id].export_api()


@get("/api/devices", dependencies={"devices": Provide(get_devices)})
async def devices(devices: Devices) -> t.List[APIDevice]:
    """Retrieve all devices."""
    return devices.export_api()


@get("/api/queries", dependencies={"devices": Provide(get_devices)})
async def queries(devices: Devices) -> t.List[str]:
    """Retrieve all directive names."""
    return devices.directive_names()


@get("/api/info", dependencies={"params": Provide(get_params)})
async def info(params: Params) -> APIParams:
    """Retrieve looking glass parameters."""
    return params.export_api()


@post("/api/query", dependencies={"_state": Provide(get_state)})
async def query(_state: HyperglassState, request: Request, data: Query) -> QueryResponse:
    """Ingest request data pass it to the backend application to perform the query."""
    import asyncio
    from functools import partial

    timestamp = datetime.now(UTC)

    # Initialize cache
    cache = _state.redis

    # Use hashed `data` string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = f"hyperglass.query.{data.digest()}"

    _log = log.bind(query=data.summary())

    _log.info("Starting query execution")

    # Wrap blocking cache operations in executor to prevent event loop blocking
    loop = asyncio.get_event_loop()
    cache_response = await loop.run_in_executor(None, partial(cache.get_map, cache_key, "output"))
    json_output = False
    cached = False
    runtime = 65535

    if cache_response:
        _log.bind(cache_key=cache_key).debug("Cache hit")

        # If a cached response exists, reset the expiration time.
        await loop.run_in_executor(
            None, partial(cache.expire, cache_key, expire_in=_state.params.cache.timeout)
        )

        cached = True
        runtime = 0
        timestamp = await loop.run_in_executor(None, partial(cache.get_map, cache_key, "timestamp"))

    elif not cache_response:
        _log.bind(cache_key=cache_key).debug("Cache miss")

        # Check if this exact query is already running
        if cache_key in _ongoing_queries:
            _log.bind(cache_key=cache_key).debug(
                "Query already in progress - waiting for completion"
            )
            # Wait for the ongoing query to complete
            await _ongoing_queries[cache_key].wait()
            # Check cache again after waiting
            cache_response = await loop.run_in_executor(
                None, partial(cache.get_map, cache_key, "output")
            )
            if cache_response:
                _log.bind(cache_key=cache_key).debug("Query completed by another request")
                cached = True
                runtime = 0
                timestamp = await loop.run_in_executor(
                    None, partial(cache.get_map, cache_key, "timestamp")
                )
            else:
                _log.bind(cache_key=cache_key).warning(
                    "Query completed but no cache found - executing anyway"
                )

        if not cache_response:
            # Mark this query as ongoing
            _ongoing_queries[cache_key] = asyncio.Event()

            try:
                timestamp = data.timestamp
                starttime = time.time()

                if _state.params.fake_output:
                    # Return fake, static data for development purposes, if enabled.
                    output = await fake_output(
                        query_type=data.query_type,
                        structured=data.device.structured_output or False,
                    )
                else:
                    # Pass request to execution module with retry logic for specific platforms
                    max_retries = 2 if data.device.platform in ("mikrotik_routeros", "mikrotik_switchos", "mikrotik") else 1
                    retry_count = 0
                    output = None
                    
                    while retry_count < max_retries:
                        attempt_start = time.time()
                        output = await execute(data)
                        attempt_time = round(time.time() - attempt_start, 4)
                        
                        # Check if this looks like a failed MikroTik query (empty result + fast execution)
                        should_retry = False
                        if retry_count < max_retries - 1 and data.device.platform in ("mikrotik_routeros", "mikrotik_switchos", "mikrotik"):
                            if is_type(output, OutputDataModel):
                                try:
                                    as_json = output.export_json()
                                    raw_output = json.loads(as_json)
                                    # Check for empty BGP route table and fast execution (< 5 seconds)
                                    if (isinstance(raw_output, dict) and 
                                        "count" in raw_output and "routes" in raw_output and
                                        raw_output.get("count", 0) == 0 and 
                                        not raw_output.get("routes") and
                                        attempt_time < 5.0):
                                        should_retry = True
                                        _log.bind(attempt=retry_count + 1, runtime=attempt_time).warning(
                                            "MikroTik returned empty result with fast execution time - retrying"
                                        )
                                except Exception:
                                    # If we can't parse the output, don't retry
                                    pass
                        
                        if not should_retry:
                            break
                            
                        retry_count += 1
                        if should_retry:
                            # Wait a bit before retrying to let the device settle
                            await asyncio.sleep(2)

                endtime = time.time()
                elapsedtime = round(endtime - starttime, 4)
                _log.debug("Runtime: {!s} seconds", elapsedtime)

                if output is None:
                    raise HyperglassError(message=_state.params.messages.general, alert="danger")

                json_output = is_type(output, OutputDataModel)

                if json_output:
                    # Export structured output as JSON string to guarantee value
                    # is serializable, then convert it back to a dict.
                    as_json = output.export_json()
                    raw_output = json.loads(as_json)
                else:
                    raw_output = str(output)

                # Detect semantically-empty structured outputs and avoid caching them.
                # Examples:
                # - BGPRouteTable: {'count': 0, 'routes': []}
                # - TracerouteResult: {'hops': []}
                skip_cache_empty = False
                try:
                    if json_output and isinstance(raw_output, dict):
                        # BGP route table empty
                        if "count" in raw_output and "routes" in raw_output:
                            if raw_output.get("count", 0) == 0 or not raw_output.get("routes"):
                                skip_cache_empty = True
                        # Traceroute result empty
                        if "hops" in raw_output and (not raw_output.get("hops")):
                            skip_cache_empty = True
                except Exception:
                    # If any unexpected shape is encountered, don't skip caching by
                    # accident — fall back to normal behavior.
                    skip_cache_empty = False

                if not skip_cache_empty:
                    # Only cache successful, non-empty results
                    await loop.run_in_executor(
                        None, partial(cache.set_map_item, cache_key, "output", raw_output)
                    )
                    await loop.run_in_executor(
                        None, partial(cache.set_map_item, cache_key, "timestamp", timestamp)
                    )
                    await loop.run_in_executor(
                        None,
                        partial(cache.expire, cache_key, expire_in=_state.params.cache.timeout),
                    )

                    _log.bind(cache_timeout=_state.params.cache.timeout).debug("Response cached")
                else:
                    _log.bind(cache_key=cache_key).warning(
                        "Structured output was empty (e.g. 0 routes / 0 hops) - skipping cache to allow immediate retry"
                    )

                runtime = int(round(elapsedtime, 0))

            except (DeviceTimeout, ResponseEmpty) as exc:
                # Don't cache timeout or empty response errors - allow immediate retry
                _log.bind(cache_key=cache_key).warning(
                    "Query failed with timeout or empty response - not caching result to allow immediate retry"
                )
                # Re-raise the exception so the error handler can process it normally
                raise exc

            finally:
                # Mark query as complete and notify waiting requests
                _ongoing_queries[cache_key].set()
                # Clean up the event after a short delay to allow waiting requests to proceed
                asyncio.create_task(_cleanup_query_event(cache_key))

    # If it does, return the cached entry
    cache_response = await loop.run_in_executor(None, partial(cache.get_map, cache_key, "output"))

    json_output = is_type(cache_response, t.Dict)
    response_format = "text/plain"

    if json_output:
        response_format = "application/json"
    _log.info("Execution completed")

    response = {
        "output": cache_response,
        "id": cache_key,
        "cached": cached,
        "runtime": runtime,
        "timestamp": timestamp,
        "format": response_format,
        "random": data.random(),
        "level": "success",
        "keywords": [],
    }

    return Response(
        response,
        background=BackgroundTask(
            send_webhook,
            params=_state.params,
            data=data,
            request=request,
            timestamp=timestamp,
        ),
    )
