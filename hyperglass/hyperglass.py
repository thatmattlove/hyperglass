"""Hyperglass Front End."""

# Standard Library Imports
import asyncio
import os
import tempfile
import time
from pathlib import Path

# Third Party Imports
import aredis
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess
from sanic import Sanic
from sanic import response as sanic_response
from sanic.exceptions import InvalidUsage
from sanic.exceptions import NotFound
from sanic.exceptions import ServerError
from sanic.exceptions import ServiceUnavailable
from sanic_limiter import Limiter
from sanic_limiter import RateLimitExceeded
from sanic_limiter import get_remote_address

# Project Imports
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
from hyperglass.render import render_html
from hyperglass.util import check_python
from hyperglass.util import cpu_count
from hyperglass.util import log

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
static_dir = Path(__file__).parent / "static" / "ui"
log.debug(f"Static Files: {static_dir}")

# Main Sanic App Definition
app = Sanic(__name__)
app.static("/ui", str(static_dir))
log.debug(app.config)

# Sanic Web Server Parameters
APP_PARAMS = {
    "host": params.general.listen_address,
    "port": params.general.listen_port,
    "debug": params.general.debug,
    "workers": cpu_count(),
    "access_log": params.general.debug,
    "auto_reload": params.general.debug,
}

# Redis Config
redis_config = {
    "host": params.general.redis_host,
    "port": params.general.redis_port,
    "decode_responses": True,
}

# Sanic-Limiter Config
query_rate = params.features.rate_limit.query.rate
query_period = params.features.rate_limit.query.period
site_rate = params.features.rate_limit.site.rate
site_period = params.features.rate_limit.site.period
rate_limit_query = f"{query_rate} per {query_period}"
rate_limit_site = f"{site_rate} per {site_period}"

log.debug(f"Query rate limit: {rate_limit_query}")
log.debug(f"Site rate limit: {rate_limit_site}")

# Redis Config for Sanic-Limiter storage
r_limiter_db = params.features.rate_limit.redis_id
r_limiter_url = "redis://{host}:{port}/{db}".format(
    host=params.general.redis_host,
    port=params.general.redis_port,
    db=params.features.rate_limit.redis_id,
)
r_cache = aredis.StrictRedis(db=params.features.cache.redis_id, **redis_config)
r_limiter = aredis.StrictRedis(db=params.features.rate_limit.redis_id, **redis_config)


async def check_redis():
    """Ensure Redis is running before starting server.

    Raises:
        HyperglassError: Raised if Redis is not running.

    Returns:
        {bool} -- True if Redis is running.
    """
    try:
        await r_cache.echo("hyperglass test")
        await r_limiter.echo("hyperglass test")
    except Exception:
        raise HyperglassError(
            f"Redis isn't running at: {redis_config['host']}:{redis_config['port']}",
            alert="danger",
        ) from None
    return True


# Verify Redis is running
asyncio.run(check_redis())

# Adds Sanic config variable for Sanic-Limiter
app.config.update(RATELIMIT_STORAGE_URL=r_limiter_url)

# Initializes Sanic-Limiter
limiter = Limiter(app, key_func=get_remote_address, global_limits=[rate_limit_site])

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


@app.middleware("request")
async def request_middleware(request):
    """Respond to OPTIONS methods."""
    if request.method == "OPTIONS":  # noqa: R503
        return sanic_response.json({"content": "ok"}, status=204)


@app.middleware("response")
async def response_middleware(request, response):
    """Add CORS headers to responses."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")


@app.route("/metrics")
@limiter.exempt
async def metrics(request):
    """Serve Prometheus metrics."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    latest = generate_latest(registry)
    return sanic_response.text(
        latest,
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
            "Content-Length": str(len(latest)),
        },
    )


@app.exception(InvalidUsage)
async def handle_frontend_errors(request, exception):
    """Handle user-facing feedback related to frontend/input errors."""
    client_addr = get_remote_address(request)
    error = exception.args[0]
    alert = error["alert"]
    log.info(error)
    count_errors.labels(
        "Front End Error",
        client_addr,
        request.json.get("query_type"),
        request.json.get("location"),
        request.json.get("target"),
    ).inc()
    log.error(f'Error: {error["message"]}, Source: {client_addr}')
    return sanic_response.json(
        {"output": error["message"], "alert": alert, "keywords": error["keywords"]},
        status=400,
    )


@app.exception(ServiceUnavailable)
async def handle_backend_errors(request, exception):
    """Handle user-facing feedback related to backend errors."""
    client_addr = get_remote_address(request)
    error = exception.args[0]
    alert = error["alert"]
    log.info(error)
    count_errors.labels(
        "Back End Error",
        client_addr,
        request.json.get("query_type"),
        request.json.get("location"),
        request.json.get("target"),
    ).inc()
    log.error(f'Error: {error["message"]}, Source: {client_addr}')
    return sanic_response.json(
        {"output": error["message"], "alert": alert, "keywords": error["keywords"]},
        status=503,
    )


@app.exception(NotFound)
async def handle_404(request, exception):
    """Render full error page for invalid URI."""
    path = request.path
    html = render_html("404", uri=path)
    client_addr = get_remote_address(request)
    count_notfound.labels(exception, path, client_addr).inc()
    log.error(f"Error: {exception}, Path: {path}, Source: {client_addr}")
    return sanic_response.html(html, status=404)


@app.exception(RateLimitExceeded)
async def handle_429(request, exception):
    """Render full error page for too many site queries."""
    html = render_html("ratelimit-site")
    client_addr = get_remote_address(request)
    count_ratelimit.labels(exception, client_addr).inc()
    log.error(f"Error: {exception}, Source: {client_addr}")
    return sanic_response.html(html, status=429)


@app.exception(ServerError)
async def handle_500(request, exception):
    """Render general error page."""
    client_addr = get_remote_address(request)
    count_errors.labels(500, exception, client_addr, None, None, None).inc()
    log.error(f"Error: {exception}, Source: {client_addr}")
    html = render_html("500")
    return sanic_response.html(html, status=500)


async def clear_cache():
    """Clear the Redis cache."""
    try:
        await r_cache.flushdb()
        return "Successfully cleared cache"
    except Exception as error_exception:
        log.error(f"Error clearing cache: {error_exception}")
        raise HyperglassError(f"Error clearing cache: {error_exception}")


@app.route("/", methods=["GET", "OPTIONS"])
@limiter.limit(rate_limit_site, error_message="Site")
async def site(request):
    """Serve main application front end."""
    html = await render_html("form", primary_asn=params.general.primary_asn)
    return sanic_response.html(html)


@app.route("/config", methods=["GET", "OPTIONS"])
async def frontend_config(request):
    """Provide validated user/default config for front end consumption.

    Returns:
        {dict} -- Filtered configuration
    """
    return sanic_response.json(frontend_params)


@app.route("/query", methods=["POST", "OPTIONS"])
@limiter.limit(
    rate_limit_query,
    error_message={
        "output": params.features.rate_limit.query.message,
        "alert": "danger",
        "keywords": [],
    },
)
async def hyperglass_main(request):
    """Process XHR POST data.

    Ingests XHR POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """
    # Get JSON data from Ajax POST
    raw_query_data = request.json
    log.debug(f"Unvalidated input: {raw_query_data}")

    # Perform basic input validation
    # query_data = await validate_input(raw_query_data)
    try:
        query_data = Query(**raw_query_data)
    except InputInvalid as he:
        raise InvalidUsage(he.__dict__())

    # Get client IP address for Prometheus logging & rate limiting
    client_addr = get_remote_address(request)

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
    cache_key = hash(query_data)

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
            raise InvalidUsage(frontend_error.__dict__())
        except (AuthError, RestError, ScrapeError, DeviceTimeout) as backend_error:
            raise ServiceUnavailable(backend_error.__dict__())

        if cache_value is None:
            raise ServerError(
                {"message": params.messages.general, "alert": "danger", "keywords": []}
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

    return sanic_response.json({"output": response_output}, status=200)
