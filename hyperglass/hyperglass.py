"""
Main Hyperglass Front End
"""
# Standard Library Imports
import json
from ast import literal_eval

# Third Party Imports
import redis
from flask import Flask
from flask import Response
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from logzero import logger
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess

# Project Imports
from hyperglass import render
from hyperglass.command.execute import Execute
from hyperglass.configuration import devices
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.configuration import params
from hyperglass.constants import Supported
from hyperglass.constants import code
from hyperglass.exceptions import HyperglassError

logger.debug(f"Configuration Parameters:\n {params.dict()}")

# Redis Config
redis_config = {
    "host": params.general.redis_host,
    "port": params.general.redis_port,
    "charset": "utf-8",
    "decode_responses": True,
}

# Main Flask definition
app = Flask(__name__, static_url_path="/static")

# Redis Cache Config
r_cache = redis.Redis(db=params.features.rate_limit.redis_id, **redis_config)

# Flask-Limiter Config
query_rate = params.features.rate_limit.query.rate
query_period = params.features.rate_limit.query.period
site_rate = params.features.rate_limit.site.rate
site_period = params.features.rate_limit.site.period
#
rate_limit_query = f"{query_rate} per {query_period}"
rate_limit_site = f"{site_rate} per {site_period}"
logger.debug(f"Query rate limit: {rate_limit_query}")
logger.debug(f"Site rate limit: {rate_limit_site}")

# Redis Config for Flask-Limiter storage
r_limiter_db = params.features.rate_limit.redis_id
r_limiter_url = f'redis://{redis_config["host"]}:{redis_config["port"]}/{r_limiter_db}'
r_limiter = redis.Redis(**redis_config, db=params.features.rate_limit.redis_id)
# Adds Flask config variable for Flask-Limiter
app.config.update(RATELIMIT_STORAGE_URL=r_limiter_url)
# Initializes Flask-Limiter
limiter = Limiter(app, key_func=get_ipaddr, default_limits=[rate_limit_site])

# Prometheus Config
count_data = Counter(
    "count_data", "Query Counter", ["source", "type", "loc_id", "target"]
)

count_errors = Counter(
    "count_errors",
    "Error Counter",
    ["code", "reason", "source", "type", "loc_id", "target"],
)

count_ratelimit = Counter(
    "count_ratelimit", "Rate Limit Counter", ["message", "source"]
)

count_notfound = Counter(
    "count_notfound", "404 Not Found Counter", ["message", "path", "source"]
)


@app.route("/metrics")
def metrics():
    """Prometheus metrics"""
    content_type_latest = str("text/plain; version=0.0.4; charset=utf-8")
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=content_type_latest)


@app.errorhandler(404)
def handle_404(e):
    """Renders full error page for invalid URI"""
    html = render.html("404")
    path = request.path
    client_addr = get_ipaddr()
    count_notfound.labels(e, path, client_addr).inc()
    logger.error(f"Error: {e}, Path: {path}, Source: {client_addr}")
    return html, 404


@app.errorhandler(429)
def handle_429(e):
    """Renders full error page for too many site queries"""
    html = render.html("429")
    client_addr = get_ipaddr()
    count_ratelimit.labels(e, client_addr).inc()
    logger.error(f"Error: {e}, Source: {client_addr}")
    return html, 429


@app.errorhandler(500)
def handle_500(e):
    """General Error Page"""
    client_addr = get_ipaddr()
    count_errors.labels(500, e, client_addr, None, None, None).inc()
    logger.error(f"Error: {e}, Source: {client_addr}")
    html = render.html("500")
    return html, 500


def clear_cache():
    """Function to clear the Redis cache"""
    try:
        r_cache.flushdb()
    except Exception as error_exception:
        logger.error(f"Error clearing cache: {error_exception}")
        raise HyperglassError(f"Error clearing cache: {error_exception}")


@app.route("/", methods=["GET"])
@limiter.limit(rate_limit_site, error_message="Site")
def site():
    """Main front-end web application"""
    return render.html("index")


@app.route("/test", methods=["GET"])
def test_route():
    """Test route for various tests"""
    html = render.html("500")
    return html, 500


@app.route("/locations/<asn>", methods=["GET"])
def get_locations(asn):
    """
    Flask GET route provides a JSON list of all locations for the
    selected network/ASN.
    """
    locations_list_json = json.dumps(devices.locations[asn])
    logger.debug(f"Locations list:{devices.locations[asn]}")
    return locations_list_json


@app.route("/lg", methods=["POST"])
# Invoke Flask-Limiter with configured rate limit
@limiter.limit(rate_limit_query, error_message="Query")
def hyperglass_main():
    """
    Main backend application initiator. Ingests Ajax POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """
    # Get JSON data from Ajax POST
    lg_data = request.get_json()
    logger.debug(f"Unvalidated input: {lg_data}")
    # Return error if no target is specified
    if not lg_data["target"]:
        logger.debug("No input specified")
        return Response(params.messages.no_input, code.invalid)
    # Return error if no location is selected
    if lg_data["location"] not in devices.hostnames:
        logger.debug("No selection specified")
        return Response(params.messages.no_location, code.invalid)
    # Return error if no query type is selected
    if not Supported.is_supported_query(lg_data["type"]):
        logger.debug("No query specified")
        return Response(params.messages.no_query_type, code.invalid)
    # Get client IP address for Prometheus logging & rate limiting
    client_addr = get_ipaddr()
    # Increment Prometheus counter
    count_data.labels(
        client_addr, lg_data["type"], lg_data["location"], lg_data["target"]
    ).inc()
    logger.debug(f"Client Address: {client_addr}")
    # Stringify the form response containing serialized JSON for the
    # request, use as key for k/v cache store so each command output
    # value is unique
    cache_key = str(lg_data)
    # Define cache entry expiry time
    cache_timeout = params.features.cache.timeout
    logger.debug(f"Cache Timeout: {cache_timeout}")
    # Check if cached entry exists
    if not r_cache.get(cache_key):
        logger.debug(f"Sending query {cache_key} to execute module...")
        # Pass request to execution module
        cache_value = Execute(lg_data).response()

        logger.debug("Validated Response...")
        logger.debug(f"Status: {cache_value[1]}")
        logger.debug(f"Output:\n {cache_value[0]}")
        # Create a cache entry
        r_cache.set(cache_key, str(cache_value))
        r_cache.expire(cache_key, cache_timeout)

        logger.debug(f"Added cache entry for query: {cache_key}")
        logger.error(f"Unable to add output to cache: {cache_key}")
    # If it does, return the cached entry
    cache_response = r_cache.get(cache_key)
    response = literal_eval(cache_response)
    response_output, response_status = response

    logger.debug(f"Cache match for: {cache_key}, returning cached entry")
    logger.debug(f"Cache Output: {response_output}")
    logger.debug(f"Cache Status Code: {response_status}")
    # If error, increment Prometheus metrics
    if response_status in [405, 415, 504]:
        count_errors.labels(
            response_status,
            code.get_reason(response_status),
            client_addr,
            lg_data["type"],
            lg_data["location"],
            lg_data["target"],
        ).inc()
    return Response(*response)
