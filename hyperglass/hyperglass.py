"""Hyperglass Front End"""

# Standard Library Imports
import operator
import time
from pathlib import Path

# Third Party Imports
import aredis
from logzero import logger
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess
from prometheus_client import CONTENT_TYPE_LATEST
from sanic import Sanic
from sanic import response
from sanic.exceptions import NotFound
from sanic.exceptions import ServerError
from sanic.exceptions import InvalidUsage
from sanic.exceptions import ServiceUnavailable
from sanic_limiter import Limiter
from sanic_limiter import RateLimitExceeded
from sanic_limiter import get_remote_address

# Project Imports
from hyperglass.render import render_html
from hyperglass.command.execute import Execute
from hyperglass.configuration import devices
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.configuration import params
from hyperglass.constants import Supported
from hyperglass.exceptions import (
    HyperglassError,
    AuthError,
    ScrapeError,
    RestError,
    InputInvalid,
    InputNotAllowed,
    DeviceTimeout,
)

logger.debug(f"Configuration Parameters:\n {params.dict()}")

# Redis Config
redis_config = {
    "host": params.general.redis_host,
    "port": params.general.redis_port,
    "decode_responses": True,
}

# Static File Definitions
static_dir = Path(__file__).parent / "static" / "ui"

# Main Sanic app definition
logger.debug(f"Static Files: {static_dir}")

app = Sanic(__name__)
app.static("/ui", str(static_dir))

logger.debug(app.config)

# Redis Cache Config
r_cache = aredis.StrictRedis(db=params.features.cache.redis_id, **redis_config)

# Sanic-Limiter Config
query_rate = params.features.rate_limit.query.rate
query_period = params.features.rate_limit.query.period
site_rate = params.features.rate_limit.site.rate
site_period = params.features.rate_limit.site.period
#
rate_limit_query = f"{query_rate} per {query_period}"
rate_limit_site = f"{site_rate} per {site_period}"
logger.debug(f"Query rate limit: {rate_limit_query}")
logger.debug(f"Site rate limit: {rate_limit_site}")

# Redis Config for Sanic-Limiter storage
r_limiter_db = params.features.rate_limit.redis_id
r_limiter_url = "redis://{host}:{port}/{db}".format(
    host=params.general.redis_host,
    port=params.general.redis_port,
    db=params.features.rate_limit.redis_id,
)
r_limiter = aredis.StrictRedis(db=params.features.rate_limit.redis_id, **redis_config)

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


@app.route("/metrics")
@limiter.exempt
async def metrics(request):
    """Prometheus metrics"""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    latest = generate_latest(registry)
    return response.text(
        latest,
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
            "Content-Length": str(len(latest)),
        },
    )


@app.exception(InvalidUsage)
async def handle_frontend_errors(request, exception):
    """Handles user-facing feedback related to frontend/input errors"""
    client_addr = get_remote_address(request)
    error = exception.args[0]
    alert = error["alert"]
    logger.info(error)
    count_errors.labels(
        "Front End Error",
        client_addr,
        request.json.get("query_type"),
        request.json.get("location"),
        request.json.get("target"),
    ).inc()
    logger.error(f'Error: {error["message"]}, Source: {client_addr}')
    return response.json(
        {"output": error["message"], "alert": alert, "keywords": error["keywords"]},
        status=400,
    )


@app.exception(ServiceUnavailable)
async def handle_backend_errors(request, exception):
    """Handles user-facing feedback related to backend errors"""
    client_addr = get_remote_address(request)
    error = exception.args[0]
    alert = error["alert"]
    logger.info(error)
    count_errors.labels(
        "Back End Error",
        client_addr,
        request.json.get("query_type"),
        request.json.get("location"),
        request.json.get("target"),
    ).inc()
    logger.error(f'Error: {error["message"]}, Source: {client_addr}')
    return response.json(
        {"output": error["message"], "alert": alert, "keywords": error["keywords"]},
        status=503,
    )


@app.exception(NotFound)
async def handle_404(request, exception):
    """Renders full error page for invalid URI"""
    path = request.path
    html = render_html("404", uri=path)
    client_addr = get_remote_address(request)
    count_notfound.labels(exception, path, client_addr).inc()
    logger.error(f"Error: {exception}, Path: {path}, Source: {client_addr}")
    return response.html(html, status=404)


@app.exception(RateLimitExceeded)
async def handle_429(request, exception):
    """Renders full error page for too many site queries"""
    html = render_html("ratelimit-site")
    client_addr = get_remote_address(request)
    count_ratelimit.labels(exception, client_addr).inc()
    logger.error(f"Error: {exception}, Source: {client_addr}")
    return response.html(html, status=429)


@app.exception(ServerError)
async def handle_500(request, exception):
    """General Error Page"""
    client_addr = get_remote_address(request)
    count_errors.labels(500, exception, client_addr, None, None, None).inc()
    logger.error(f"Error: {exception}, Source: {client_addr}")
    html = render_html("500")
    return response.html(html, status=500)


async def clear_cache():
    """Function to clear the Redis cache"""
    try:
        await r_cache.flushdb()
        return "Successfully cleared cache"
    except Exception as error_exception:
        logger.error(f"Error clearing cache: {error_exception}")
        raise HyperglassError(f"Error clearing cache: {error_exception}")


@app.route("/", methods=["GET"])
@limiter.limit(rate_limit_site, error_message="Site")
async def site(request):
    """Main front-end web application"""
    return response.html(render_html("form", primary_asn=params.general.primary_asn))


@app.route("/test", methods=["GET"])
async def test_route(request):
    """Test route for various tests"""
    html = render_html("500")
    return response.html(html, status=500)


async def validate_input(query_data):  # noqa: C901
    """
    Deletes any globally unsupported query parameters.
    
    Performs validation functions per input type:
        - query_target:
            - Verifies input is not empty
            - Verifies input is a string
        - query_location:
            - Verfies input is not empty
            - Verifies input is a list
            - Verifies locations in list are defined
        - query_type:
            - Verifies input is not empty
            - Verifies input is a string
            - Verifies query type is enabled and supported
        - query_vrf: (if feature enabled)
            - Verfies input is a list
            - Verifies VRFs in list are defined
    """
    # Delete any globally unsupported parameters
    for (param, value) in query_data:
        if param not in Supported.query_parameters:
            query_data.pop(param, None)

    # Unpack query data
    query_location = query_data.get("query_location", [])
    query_type = query_data.get("query_type", "")
    query_target = query_data.get("query_target", "")
    query_vrf = query_data.get("query_vrf", [])

    # Verify that query_target is not empty
    if not query_target:
        logger.debug("No input specified")
        raise InvalidUsage(
            {
                "message": params.messages.no_input.format(
                    query_type=params.branding.text.query_target
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_target],
            }
        )
    # Verify that query_target is a string
    if not isinstance(query_target, str):
        logger.debug("Target is not a string")
        raise InvalidUsage(
            {
                "message": params.messages.invalid_target.format(
                    query_target=query_target
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_target, query_target],
            }
        )
    # Verify that query_location is not empty
    if not query_location:
        logger.debug("No selection specified")
        raise InvalidUsage(
            {
                "message": params.messages.no_input.format(
                    query_type=params.branding.text.query_location
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location],
            }
        )
    # Verify that query_location is a list
    if not isinstance(query_location, list):
        logger.debug("Query Location is not a list/array")
        raise InvalidUsage(
            {
                "message": params.messages.invalid_location.format(
                    query_location=params.branding.text.query_location
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location, query_location],
            }
        )
    # Verify that locations in query_location are actually defined
    if not all(loc in query_location for loc in devices.hostnames):
        raise InvalidUsage(
            {
                "message": params.messages.invalid_location.format(
                    query_location=params.branding.text.query_location
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location, query_location],
            }
        )
    # Verify that query_type is not empty
    if not query_type:
        logger.debug("No query specified")
        raise InvalidUsage(
            {
                "message": params.messages.no_input.format(
                    query_type=params.branding.text.query_type
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location],
            }
        )
    if not isinstance(query_type, str):
        logger.debug("Query Type is not a string")
        raise InvalidUsage(
            {
                "message": params.messages.invalid_location.format(
                    query_location=params.branding.text.query_location
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location, query_location],
            }
        )
    # Verify that query_type is actually supported
    query_is_supported = Supported.is_supported_query(query_type)
    if not query_is_supported:
        logger.debug("Query not supported")
        raise InvalidUsage(
            {
                "message": params.messages.invalid_query_type.format(
                    query_type=query_type, name=params.branding.text.query_type
                ),
                "alert": "warning",
                "keywords": [params.branding.text.query_location, query_type],
            }
        )
    elif query_is_supported:
        query_is_enabled = operator.attrgetter(f"{query_type}.enable")(params.features)
        if not query_is_enabled:
            raise InvalidUsage(
                {
                    "message": params.messages.invalid_query_type.format(
                        query_type=query_type, name=params.branding.text.query_type
                    ),
                    "alert": "warning",
                    "keywords": [params.branding.text.query_location, query_type],
                }
            )
    if params.features.vrf.enable:
        # Verify that query_vrf is a list
        if query_vrf and not isinstance(query_vrf, list):
            raise InvalidUsage(
                {
                    "message": params.messages.invalid_query_vrf.format(
                        query_vrf=query_vrf, name=params.branding.text.query_vrf
                    ),
                    "alert": "warning",
                    "keywords": [params.branding.text.query_vrf, query_vrf],
                }
            )
        # Verify that vrfs in query_vrf are defined
        if query_vrf and not all(vrf in query_vrf for vrf in devices.vrfs):
            raise InvalidUsage(
                {
                    "message": params.messages.invalid_query_vrf.format(
                        query_vrf=query_vrf, name=params.branding.text.query_vrf
                    ),
                    "alert": "warning",
                    "keywords": [params.branding.text.query_vrf, query_vrf],
                }
            )
    return query_data


@app.route("/query", methods=["POST"])
@limiter.limit(
    rate_limit_query,
    error_message={
        "output": params.features.rate_limit.query.message,
        "alert": "danger",
        "keywords": [],
    },
)
async def hyperglass_main(request):
    """
    Main backend application initiator. Ingests Ajax POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """
    # Get JSON data from Ajax POST
    raw_query_data = request.json
    logger.debug(f"Unvalidated input: {raw_query_data}")

    # Perform basic input validation
    query_data = validate_input(raw_query_data)

    # Get client IP address for Prometheus logging & rate limiting
    client_addr = get_remote_address(request)

    # Increment Prometheus counter
    count_data.labels(
        client_addr,
        query_data.get("query_type"),
        query_data.get("query_location"),
        query_data.get("query_target"),
        query_data.get("query_vrf"),
    ).inc()

    logger.debug(f"Client Address: {client_addr}")

    # Stringify the form response containing serialized JSON for the
    # request, use as key for k/v cache store so each command output
    # value is unique
    cache_key = str(query_data)

    # Define cache entry expiry time
    cache_timeout = params.features.cache.timeout
    logger.debug(f"Cache Timeout: {cache_timeout}")

    # Check if cached entry exists
    if not await r_cache.get(cache_key):
        logger.debug(f"Sending query {cache_key} to execute module...")

        # Pass request to execution module
        try:
            starttime = time.time()

            cache_value = await Execute(query_data).response()

            endtime = time.time()
            elapsedtime = round(endtime - starttime, 4)

            logger.debug(f"Query {cache_key} took {elapsedtime} seconds to run.")

        except (InputInvalid, InputNotAllowed) as frontend_error:
            raise InvalidUsage(frontend_error.__dict__())
        except (AuthError, RestError, ScrapeError, DeviceTimeout) as backend_error:
            raise ServiceUnavailable(backend_error.__dict__())

        if not cache_value:
            raise ServerError(
                {"message": params.messages.general, "alert": "danger", "keywords": []}
            )

        # Create a cache entry
        await r_cache.set(cache_key, str(cache_value))
        await r_cache.expire(cache_key, cache_timeout)

        logger.debug(f"Added cache entry for query: {cache_key}")

    # If it does, return the cached entry
    cache_response = await r_cache.get(cache_key)

    response_output = cache_response

    logger.debug(f"Cache match for: {cache_key}, returning cached entry")
    logger.debug(f"Cache Output: {response_output}")

    return response.json({"output": response_output}, status=200)
