# https://github.com/checktheroads/hyperglass
"""
Main Hyperglass Front End
"""
# Standard Imports
import json
import logging
from pprint import pprint

# Module Imports
import logzero
from logzero import logger
from flask import Flask, request, Response
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from prometheus_client import generate_latest, Counter

# Project Imports
from hyperglass.command import execute
from hyperglass import configuration
from hyperglass import render

# Main Flask definition
app = Flask(__name__, static_url_path="/static")

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)

# Initialize general configuration parameters for reuse
# brand = configuration.branding()
config = configuration.params()
codes = configuration.codes()
codes_reason = configuration.codes_reason()
logger.debug(f"Configuration Parameters:\n {pprint(config)}")

# Flask-Limiter Config
query_rate = config["features"]["rate_limit"]["query"]["rate"]
query_period = config["features"]["rate_limit"]["query"]["period"]
site_rate = config["features"]["rate_limit"]["site"]["rate"]
site_period = config["features"]["rate_limit"]["site"]["period"]
rate_limit_query = f"{query_rate} per {query_period}"
rate_limit_site = f"{site_rate} per {site_period}"
limiter = Limiter(app, key_func=get_ipaddr, default_limits=[rate_limit_site])
logger.debug(f"Query rate limit: {rate_limit_query}")
logger.debug(f"Site rate limit: {rate_limit_site}")

# Flask-Caching Config
cache_directory = config["features"]["cache"]["directory"]
cache_timeout = config["features"]["cache"]["timeout"]
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": cache_directory,
        "CACHE_DEFAULT_TIMEOUT": cache_timeout,
    },
)
logger.debug(f"Cache directory: {cache_directory}, Cache timeout: {cache_timeout}")

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


@app.route("/metrics")
def metrics():
    """Prometheus metrics"""
    content_type_latest = str("text/plain; version=0.0.4; charset=utf-8")
    return Response(generate_latest(), mimetype=content_type_latest)


@app.errorhandler(404)
def handle_404(e):
    """Renders full error page for too many site queries"""
    html = render.html("404")
    count_ratelimit.labels(e, get_ipaddr()).inc()
    logger.error(e)
    return html, 404


@app.errorhandler(429)
def handle_429(e):
    """Renders full error page for too many site queries"""
    html = render.html("429")
    count_ratelimit.labels(e, get_ipaddr()).inc()
    logger.error(e)
    return html, 429


@app.errorhandler(500)
def handle_500(e):
    """General Error Page"""
    count_errors.labels(500, e, get_ipaddr(), None, None, None).inc()
    logger.error(e)
    html = render.html("500")
    return html, 500


def clear_cache():
    """Function to clear the Flask-Caching cache"""
    with app.app_context():
        try:
            cache.clear()
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
    if lg_data["location"] not in configuration.locations():
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
    client_addr = request.remote_addr
    count_data.labels(
        client_addr, lg_data["type"], lg_data["location"], lg_data["target"]
    ).inc()
    logger.debug(f"Client Address: {client_addr}")
    # Stringify the form response containing serialized JSON for the request, use as key for k/v
    # cache store so each command output value is unique
    cache_key = str(lg_data)
    # Check if cached entry exists
    if cache.get(cache_key) is None:
        try:
            logger.debug(f"Sending query {cache_key} to execute module...")
            cache_value = execute.Execute(lg_data).response()
            logger.debug(f"Validated response...")
            value_code = cache_value[1]
            value_entry = cache_value[0:2]
            logger.debug(
                f"Status Code: {value_code}, Output: {cache_value[1]}, Info: {cache_value[2]}"
            )
            # If it doesn't, create a cache entry
            cache.set(cache_key, value_entry)
            logger.debug(f"Added cache entry for query: {cache_key}")
            # If 200, return output
            response = cache.get(cache_key)
            if value_code == 200:
                logger.debug(f"Returning {value_code} response")
                return Response(response[0], response[1])
            # If 400 error, return error message and code
            # Note: 200 & 400 errors are separated mainly for potential future use
            if value_code in [405, 415]:
                count_errors.labels(
                    response[1],
                    codes_reason[response[1]],
                    client_addr,
                    lg_data["type"],
                    lg_data["location"],
                    lg_data["target"],
                ).inc()
                logger.debug(f"Returning {value_code} response")
                return Response(response[0], response[1])
        except:
            logger.error(f"Unable to add output to cache: {cache_key}")
            raise
    # If it does, return the cached entry
    else:
        logger.debug(f"Cache match for: {cache_key}, returning cached entry")
        response = cache.get(cache_key)
    return Response(response[0], response[1])
