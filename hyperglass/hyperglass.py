# https://github.com/checktheroads/hyperglass
"""
Main Hyperglass Front End
"""
# Standard Imports
import json
import logging

# Module Imports
import redis
import logzero
from logzero import logger
from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from prometheus_client import generate_latest, Counter, CollectorRegistry, multiprocess

# Project Imports
from hyperglass.command import execute
from hyperglass import configuration
from hyperglass import render

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)

# Initialize general configuration parameters for reuse
config = configuration.params()
codes = configuration.codes()
codes_reason = configuration.codes_reason()
logger.debug(f"Configuration Parameters:\n {config}")

# Redis Config
redis_config = {
    "host": config["general"]["redis_host"],
    "port": config["general"]["redis_port"],
    "charset": "utf-8",
    "decode_responses": True,
}

# Main Flask definition
app = Flask(__name__, static_url_path="/static")

# Redis Cache Config
r_cache = redis.Redis(**redis_config, db=config["features"]["rate_limit"]["redis_id"])

# Flask-Limiter Config
query_rate = config["features"]["rate_limit"]["query"]["rate"]
query_period = config["features"]["rate_limit"]["query"]["period"]
site_rate = config["features"]["rate_limit"]["site"]["rate"]
site_period = config["features"]["rate_limit"]["site"]["period"]
rate_limit_query = f"{query_rate} per {query_period}"
rate_limit_site = f"{site_rate} per {site_period}"
logger.debug(f"Query rate limit: {rate_limit_query}")
logger.debug(f"Site rate limit: {rate_limit_site}")

# Redis Config for Flask-Limiter storage
r_limiter_db = config["features"]["rate_limit"]["redis_id"]
r_limiter_url = f'redis://{redis_config["host"]}:{redis_config["port"]}/{r_limiter_db}'
r_limiter = redis.Redis(**redis_config, db=config["features"]["rate_limit"]["redis_id"])
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
        raise


@app.route("/", methods=["GET"])
@limiter.limit(rate_limit_site, error_message="Site")
def site():
    """Main front-end web application"""
    html = render.html("index")
    return html


@app.route("/test", methods=["GET"])
def test_route():
    """Test route for various tests"""
    html = render.html("500")
    return html, 500


@app.route("/locations/<asn>", methods=["GET"])
def get_locations(asn):
    """Flask GET route provides a JSON list of all locations for the selected network/ASN"""
    locations_list = configuration.locations_list()
    locations_list_json = json.dumps(locations_list[asn])
    logger.debug(f"Locations list:\n{locations_list}")
    return locations_list_json


@app.route("/lg", methods=["POST"])
# Invoke Flask-Limiter with configured rate limit
@limiter.limit(rate_limit_query, error_message="Query")
def hyperglass_main():
    """Main backend application initiator. Ingests Ajax POST data from form submit, passes it to
    the backend application to perform the filtering/lookups"""
    # Get JSON data from Ajax POST
    lg_data = request.get_json()
    logger.debug(f"Unvalidated input: {lg_data}")
    # Return error if no target is specified
    if not lg_data["target"]:
        logger.debug("No input specified")
        return Response(config["messages"]["no_input"], codes["danger"])
    # Return error if no location is selected
    if lg_data["location"] not in configuration.hostnames():
        logger.debug("No selection specified")
        return Response(config["messages"]["no_location"], codes["danger"])
    # Return error if no query type is selected
    if lg_data["type"] not in [
        "bgp_route",
        "bgp_community",
        "bgp_aspath",
        "ping",
        "traceroute",
    ]:
        logger.debug("No query specified")
        return Response(config["messages"]["no_query_type"], codes["danger"])
    client_addr = get_ipaddr()
    count_data.labels(
        client_addr, lg_data["type"], lg_data["location"], lg_data["target"]
    ).inc()
    logger.debug(f"Client Address: {client_addr}")
    # Stringify the form response containing serialized JSON for the request, use as key for k/v
    # cache store so each command output value is unique
    cache_key = str(lg_data)
    # Define cache entry expiry time
    cache_timeout = config["features"]["cache"]["timeout"]
    logger.debug(f"Cache Timeout: {cache_timeout}")
    # Check if cached entry exists
    if not r_cache.hgetall(cache_key):
        try:
            logger.debug(f"Sending query {cache_key} to execute module...")
            cache_value = execute.Execute(lg_data).response()
            value_output = cache_value["output"]
            value_code = cache_value["status"]
            logger.debug(
                f"Validated response...\nStatus Code: {value_code}, Output: {value_output}"
            )
            # If it doesn't, create a cache entry
            r_cache.hmset(cache_key, cache_value)
            r_cache.expire(cache_key, cache_timeout)
            logger.debug(f"Added cache entry for query: {cache_key}")
            # If 200, return output
            response = r_cache.hgetall(cache_key)
            if value_code == 200:
                logger.debug(f"Returning {value_code} response")
                return Response(response["output"], response["status"])
            # If 400 error, return error message and code
            if value_code in [405, 415]:
                count_errors.labels(
                    response["status"],
                    codes_reason[response["status"]],
                    client_addr,
                    lg_data["type"],
                    lg_data["location"],
                    lg_data["target"],
                ).inc()
                logger.debug(f"Returning {value_code} response")
                return Response(response["output"], response["status"])
        except:
            logger.error(f"Unable to add output to cache: {cache_key}")
            raise
    # If it does, return the cached entry
    else:
        logger.debug(f"Cache match for: {cache_key}, returning cached entry")
        response = r_cache.hgetall(cache_key)
    return Response(response["output"], response["status"])
