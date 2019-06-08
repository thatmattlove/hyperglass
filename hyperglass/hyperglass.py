# https://github.com/checktheroads/hyperglass
"""
Main Hyperglass Front End
"""
# Module Imports
import json
from logzero import logger
from flask import Flask, request, Response
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from prometheus_client import generate_latest, Counter

# Project Imports
import hyperglass.configuration as configuration
from hyperglass.command import execute
from hyperglass import render

# Main Flask definition
app = Flask(__name__, static_url_path="/static")

# Initialize general configuration parameters for reuse
general = configuration.general()
codes_reason = configuration.codes_reason()

# Flask-Limiter Config
rate_limit_query = f'{general["rate_limit_query"]} per minute'
rate_limit_site = f'{general["rate_limit_site"]} per minute'
limiter = Limiter(app, key_func=get_ipaddr, default_limits=[rate_limit_site])

# Flask-Caching Config
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": general["cache_directory"],
        "CACHE_DEFAULT_TIMEOUT": general["cache_timeout"],
    },
)

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
    CONTENT_TYPE_LATEST = str("text/plain; version=0.0.4; charset=utf-8")
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.errorhandler(429)
def error429(e):
    """Renders full error page for too many site queries"""
    html = render.html("429")
    count_ratelimit.labels(e, get_ipaddr()).inc()
    logger.error(f"{e}")
    return html, 429


@app.errorhandler(500)
def general_error():
    """General Error Page"""
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
    return html


@app.route("/routers/<asn>", methods=["GET"])
def get_routers(asn):
    """Flask GET route provides a JSON list of all routers for the selected network/ASN"""
    networks_list = configuration.networks_list()
    networks_list_json = json.dumps(networks_list[asn])
    return networks_list_json


@app.route("/lg", methods=["POST"])
# Invoke Flask-Limiter with configured rate limit
@limiter.limit(rate_limit_query, error_message="Query")
def hyperglass_main():
    """Main backend application initiator. Ingests Ajax POST data from form submit, passes it to
    the backend application to perform the filtering/lookups"""
    # Get JSON data from Ajax POST
    lg_data = request.get_json()
    client_addr = request.remote_addr
    count_data.labels(
        client_addr, lg_data["cmd"], lg_data["router"], lg_data["ipprefix"]
    ).inc()
    # Stringify the form response containing serialized JSON for the request, use as key for k/v
    # cache store so each command output value is unique
    cache_key = str(lg_data)
    # Check if cached entry exists
    if cache.get(cache_key) is None:
        try:
            cache_value = execute.Execute(lg_data).response()
            logger.info(f"Cache Value: {cache_value}")
            value_code = cache_value[1]
            value_entry = cache_value[0:2]
            value_params = cache_value[2:]
            logger.info(f"No cache match for: {cache_key}")
            # If it doesn't, create a cache entry
            cache.set(cache_key, value_entry)
            logger.info(f"Added cache entry: {value_params}")
            # If 200, return output
            response = cache.get(cache_key)
            if value_code == 200:
                return Response(response[0], response[1])
            # If 400 error, return error message and code
            # Note: 200 & 400 errors are separated mainly for potential future use
            if value_code in [405, 415]:
                count_errors.labels(
                    response[1],
                    codes_reason[response[1]],
                    client_addr,
                    lg_data["cmd"],
                    lg_data["router"],
                    lg_data["ipprefix"],
                ).inc()
                return Response(response[0], response[1])
            if value_code == 500:
                count_errors.labels(
                    response[1],
                    codes_reason[response[1]],
                    client_addr,
                    lg_data["cmd"],
                    lg_data["router"],
                    lg_data["ipprefix"],
                ).inc()
                return Response(general["msg_error_general"], 500)
        except:
            logger.error(f"Unable to add output to cache: {cache_key}")
            raise
    # If it does, return the cached entry
    else:
        logger.info(f"Cache match for: {cache_key}, returning cached entry...")
        response = cache.get(cache_key)
    return Response(response[0], response[1])
