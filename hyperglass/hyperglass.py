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

# Main Flask definition
app = Flask(__name__, static_url_path="/static")

general = configuration.general()
# Flask-Limiter Config
rate_limit_query = f"{general.rate_limit_query} per minute"
rate_limit_site = f"{general.rate_limit_site} per minute"
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
        "CACHE_DIR": general.cache_directory,
        "CACHE_DEFAULT_TIMEOUT": general.cache_timeout,
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
    nl = configuration.networks_list()
    nl_json = json.dumps(nl[asn])
    return nl_json


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
        try:
            cache_value = execute.execute(lg_data)
            value_output = cache_value[0]
            value_code = cache_value[1]
            value_entry = cache_value[0:2]
            value_params = cache_value[2:]
            logger.info(f"No cache match for: {cache_key}")
            # If it doesn't, create a cache entry
            cache.set(cache_key, value_entry)
            logger.info(f"Added cache entry: {value_params}")
        except:
            logger.error(f"Unable to add output to cache: {cache_key}")
            raise
        # If 200, return output
        response = cache.get(cache_key)
        if value_code == 200:
            try:
                return Response(response[0], response[1])
            except:
                raise
        # If 400 error, return error message and code
        elif value_code in [405, 415]:
            try:
                return Response(response[0], response[1])
            except:
                raise
    # If it does, return the cached entry
    else:
        logger.info(f"Cache match for: {cache_key}, returning cached entry...")
        response = cache.get(cache_key)
        try:
            return Response(response[0], response[1])
        except:
            raise
            # Upon exception, render generic error
            log.error(f"Error returning cached entry for: {cache_key}")
            return Response(errorGeneral(4152))
