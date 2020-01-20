"""Hyperglass Front End."""

# Standard Library Imports
import os
import tempfile
import time
from pathlib import Path

# Third Party Imports
import aredis
from fastapi import FastAPI
from fastapi import HTTPException
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.responses import UJSONResponse
from starlette.staticfiles import StaticFiles

# Project Imports
from hyperglass import __version__
from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.exceptions import AuthError
from hyperglass.exceptions import DeviceTimeout
from hyperglass.exceptions import HyperglassError
from hyperglass.exceptions import InputInvalid
from hyperglass.exceptions import InputNotAllowed
from hyperglass.exceptions import ResponseEmpty
from hyperglass.exceptions import RestError
from hyperglass.exceptions import ScrapeError
from hyperglass.execution.execute import Execute
from hyperglass.models.query import Query
from hyperglass.util import check_python
from hyperglass.util import log
from hyperglass.util import write_env

# Verify Python version meets minimum requirement
try:
    python_version = check_python()
    log.info(f"Python {python_version} detected")
except RuntimeError as r:
    raise HyperglassError(str(r), alert="danger") from None

log.debug(f"Configuration Parameters: {params.dict(by_alias=True)}")

tempdir = tempfile.TemporaryDirectory(prefix="hyperglass_")
os.environ["prometheus_multiproc_dir"] = tempdir.name

# Static File Definitions
STATIC_DIR = Path(__file__).parent / "static"
UI_DIR = STATIC_DIR / "ui"
IMAGES_DIR = STATIC_DIR / "images"
NEXT_DIR = UI_DIR / "_next"
log.debug(f"Static Files: {STATIC_DIR}")

docs_mode_map = {"swagger": "docs_url", "redoc": "redoc_url"}

docs_config = {"docs_url": None, "redoc_url": None}

if params.general.docs.enable:
    if params.general.docs.mode == "swagger":
        docs_config["docs_url"] = params.general.docs.uri
        docs_config["redoc_url"] = None
    elif params.general.docs.mode == "redoc":
        docs_config["docs_url"] = None
        docs_config["redoc_url"] = params.general.docs.uri


# Main App Definition
app = FastAPI(
    debug=params.general.debug,
    title=params.general.site_title,
    description=params.general.site_description,
    version=__version__,
    **docs_config,
)
app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")
app.mount("/_next", StaticFiles(directory=NEXT_DIR), name="_next")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/ui/images", StaticFiles(directory=IMAGES_DIR), name="ui/images")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=params.general.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASGI_PARAMS = {
    "host": str(params.general.listen_address),
    "port": params.general.listen_port,
    "debug": params.general.debug,
}

# Redis Config
redis_config = {
    "host": str(params.general.redis_host),
    "port": params.general.redis_port,
    "decode_responses": True,
}

r_cache = aredis.StrictRedis(db=params.features.cache.redis_id, **redis_config)


@app.on_event("startup")
async def check_redis():
    """Ensure Redis is running before starting server.

    Raises:
        HyperglassError: Raised if Redis is not running.

    Returns:
        {bool} -- True if Redis is running.
    """
    redis_host = redis_config["host"]
    redis_port = redis_config["port"]
    try:
        await r_cache.echo("hyperglass test")
    except Exception:
        raise HyperglassError(
            f"Redis isn't running at: {redis_host}:{redis_port}", alert="danger"
        ) from None
    log.debug(f"Redis is running at: {redis_host}:{redis_port}")
    return True


@app.on_event("startup")
async def write_env_variables():
    """Write environment varibles for Next.js/Node.

    Returns:
        {bool} -- True if successful
    """
    result = await write_env({"NODE_ENV": "production", "_HYPERGLASS_URL_": "/"})
    if result:
        log.debug(result)
    return True


# Prometheus Config
count_data = Counter(
    "count_data", "Query Counter", ["source", "query_type", "loc_id", "target", "vrf"]
)

count_errors = Counter(
    "count_errors",
    "Error Counter",
    ["reason", "source", "query_type", "loc_id", "target"],
)

count_ratelimit = Counter(
    "count_ratelimit", "Rate Limit Counter", ["message", "source"]
)

count_notfound = Counter(
    "count_notfound", "404 Not Found Counter", ["message", "path", "source"]
)


@app.get("/metrics")
async def metrics(request):
    """Serve Prometheus metrics."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    latest = generate_latest(registry)
    return PlainTextResponse(
        latest,
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
            "Content-Length": str(len(latest)),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle web server errors."""
    return UJSONResponse(
        {"output": exc.detail, "alert": "danger", "keywords": []},
        status_code=exc.status_code,
    )


@app.exception_handler(HyperglassError)
async def http_exception_handler(request, exc):
    """Handle application errors."""
    return UJSONResponse(
        {"output": exc.message, "alert": exc.alert, "keywords": exc.keywords},
        status_code=400,
    )


async def clear_cache():
    """Clear the Redis cache."""
    try:
        await r_cache.flushdb()
        return "Successfully cleared cache"
    except Exception as error_exception:
        log.error(f"Error clearing cache: {error_exception}")
        raise HyperglassError(f"Error clearing cache: {error_exception}")


@app.get("/config")
async def frontend_config():
    """Provide validated user/default config for front end consumption.

    Returns:
        {dict} -- Filtered configuration
    """
    return UJSONResponse(frontend_params, status_code=200)


@app.post("/query/")
async def hyperglass_main(query_data: Query, request: Request):
    """Process XHR POST data.

    Ingests XHR POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """

    # Get client IP address for Prometheus logging & rate limiting
    client_addr = request.client.host

    # Increment Prometheus counter
    count_data.labels(
        client_addr,
        query_data.query_type,
        query_data.query_location,
        query_data.query_target,
        query_data.query_vrf,
    ).inc()

    log.debug(f"Client Address: {client_addr}")

    # Use hashed query_data string as key for for k/v cache store so
    # each command output value is unique.
    cache_key = hash(str(query_data))

    # Define cache entry expiry time
    cache_timeout = params.features.cache.timeout
    log.debug(f"Cache Timeout: {cache_timeout}")

    # Check if cached entry exists
    if not await r_cache.get(cache_key):
        log.debug(f"Created new cache key {cache_key} entry for query {query_data}")
        log.debug("Beginning query execution...")

        # Pass request to execution module
        try:
            starttime = time.time()

            cache_value = await Execute(query_data).response()

            endtime = time.time()
            elapsedtime = round(endtime - starttime, 4)

            log.debug(f"Query {cache_key} took {elapsedtime} seconds to run.")

        except (InputInvalid, InputNotAllowed, ResponseEmpty) as frontend_error:
            raise HTTPException(detail=frontend_error.dict(), status_code=400)
        except (AuthError, RestError, ScrapeError, DeviceTimeout) as backend_error:
            raise HTTPException(detail=backend_error.dict(), status_code=500)

        if cache_value is None:
            raise HTTPException(
                detail={
                    "message": params.messages.general,
                    "alert": "danger",
                    "keywords": [],
                },
                status_code=500,
            )

        # Create a cache entry
        await r_cache.set(cache_key, str(cache_value))
        await r_cache.expire(cache_key, cache_timeout)

        log.debug(f"Added cache entry for query: {cache_key}")

    # If it does, return the cached entry
    cache_response = await r_cache.get(cache_key)

    response_output = cache_response

    log.debug(f"Cache match for: {cache_key}, returning cached entry")
    log.debug(f"Cache Output: {response_output}")

    return UJSONResponse(
        {"output": response_output},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
    )
