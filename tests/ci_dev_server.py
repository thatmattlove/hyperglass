#!/usr/bin/env python3
"""
Starts hyperglass with the Sanic web server
"""
import os
import sys
import json
from logzero import logger

working_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(working_directory)


def construct_test(test_query, location, test_target):
    """Constructs JSON POST data for test_hyperglass function."""
    constructed_query = json.dumps(
        {"type": test_query, "location": location, "target": test_target}
    )
    return constructed_query


def test_server(host, port):
    """Starts Sanic web server for testing."""
    try:
        sys.path.insert(0, parent_directory)

        from hyperglass import render
        from hyperglass import hyperglass

        render.css()
        logger.info("Starting Sanic web server...")
        hyperglass.app.run(host=host, debug=True, port=port)
    except:
        logger.error("Exception occurred while trying to start test server...")
        raise


if __name__ == "__main__":
    test_server("localhost", 5000)
