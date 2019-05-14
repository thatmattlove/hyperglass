#!/usr/bin/env python3

# Module Imports
import os
import sys
import json
import toml
from logzero import logger
from flask import Flask, request, Response, jsonify, flash
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Local Imports
import hyperglass.configuration as configuration
from hyperglass.command import execute
from hyperglass import render

# Load TOML config file
devices = configuration.devices()
# Filter config file to list of routers & subsequent configurations
routers_list = devices["router"]
# Filter config file to array of operating systems that require IPv6 BGP lookups in CIDR format
ipv6_cidr_list = configuration.requires_ipv6_cidr()
# Main Flask definition
app = Flask(__name__, static_url_path="/static")

# Flask-Limiter Config
rate_limit_query = configuration.gen.rate_limit_query() + " per minute"
rate_limit_site = configuration.gen.rate_limit_site() + "per minute"
limiter = Limiter(app, key_func=get_remote_address, default_limits=[rate_limit_site])


def renderCSS():
    try:
        render.css.renderTemplate()
    except:
        raise


# Render Main Flask-Limiter Error Message
@app.errorhandler(429)
def error429(e):
    """Renders full error page for too many site queries"""
    html = render.html.renderTemplate("429")
    return html, 429


def error415():
    """Renders full error page for generic errors"""
    html = render.html.renderTemplate("415")
    return html, 415


def errorQuery():
    """Renders modal error message"""
    return 429


def errorGeneral(id):
    """Renders notification error message with an ID number"""
    return "An unknown error occurred." + "\s" + id, 415


# Flask-Caching Config
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": configuration.gen.cache_directory(),
        "CACHE_DEFAULT_TIMEOUT": configuration.gen.cache_timeout(),
    },
)


def clearCache():
    """Function to clear the Flask-Caching cache"""
    with app.app_context():
        try:
            cache.clear()
        except:
            raise


# Main / Flask route where html is rendered via Jinja2
@app.route("/", methods=["GET"])
@limiter.limit(rate_limit_site)
def site():
    """Main front-end web application"""
    html = render.html.renderTemplate("index")
    return html


# Test route for various tests
@app.route("/test", methods=["GET"])
def testRoute():
    html = render.html.renderTemplate("test")
    return html


# Flask GET route provides a JSON list of all routers for the selected network/ASN
@app.route("/routers/<asn>", methods=["GET"])
def get_routers(asn):
    results = []
    # For any configured router matching the queried ASN, return only the address/hostname, location, and OS type of the matching routers
    for r in routers_list:
        if r["asn"] == asn:
            if r["type"] in ipv6_cidr_list:
                results.append(
                    dict(
                        location=r["location"],
                        hostname=r["name"],
                        type=r["type"],
                        requiresIP6Cidr=True,
                    )
                )
            else:
                results.append(
                    dict(
                        location=r["location"],
                        hostname=r["name"],
                        type=r["type"],
                        requiresIP6Cidr=False,
                    )
                )
        results_json = json.dumps(results)
    return results_json


# Flask POST route ingests data from the JS form submit, passes it to the backend looking glass application to perform the filtering/lookups
@app.route("/lg", methods=["POST"])
# Invoke Flask-Limiter with configured rate limit
@limiter.limit(rate_limit_query)
def lg():
    """Main backend application initiator"""
    lg_data = request.get_json()
    # Stringify the form response containing serialized JSON for the request, use as key for k/v cache store so each command output value is unique
    cache_key = str(lg_data)
    # Check if cached entry exists
    if cache.get(cache_key) is None:
        cache_value = execute.execute(lg_data)
        value_output = cache_value[0]
        value_code = cache_value[1]
        value_params = cache_value[2:]
        logger.info(f"No cache match for: {cache_key}")
        # If it doesn't, create a cache entry
        try:
            cache.set(cache_key, value_output)
            logger.info(f"Added cache entry: {value_params}")
        except:
            raise RuntimeError("Unable to add output to cache.", 415, *value_params)
        # If 200, return output
        response = cache.get(cache_key)
        if value_code == 200:
            return Response(cache.get(cache_key), value_code)
        # If 400 error, return error message and code
        elif value_code in [405, 415]:
            return Response(cache.get(cache_key), value_code)
    # If it does, return the cached entry
    else:
        logger.info(f"Cache match for: {cache_key}, returning cached entry...")
        try:
            return Response(cache.get(cache_key), value_code)
        except:
            id = 4152
            raise RuntimeError(
                id + ":\s" + "Unable to return cached output.", 415, *value_params
            )
            # Upon exception, render generic error
            return Response(errorGeneral(id))
