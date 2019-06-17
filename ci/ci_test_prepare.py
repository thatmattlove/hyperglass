#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import requests
from logzero import logger

working_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(working_directory)


def ci_config():
    """Copies test configuration files to usable config files"""
    logger.info("Migrating test config files...")
    config_dir = os.path.join(parent_directory, "hyperglass/configuration/")
    test_files = glob.iglob(os.path.join(working_directory, "*.toml"))
    config_files = glob.iglob(os.path.join(config_dir, "*.toml"))
    logger.debug(config_dir)
    logger.debug(working_directory)
    logger.debug(parent_directory)
    status = False
    for f in config_files:
        if os.path.exists(f):
            logger.debug(f"{f} already exists")
            os.remove(f)
            logger.debug(f"Deleted {f}")
    for f in test_files:
        try:
            shutil.copy(f, config_dir)
            logger.debug(f"Copied {f}")
            logger.info("Successfully migrated test config files")
            status = True
        except:
            logger.error(f"Failed to migrate {f}")
            raise
    return status


def construct_test(test_query, location, test_target):
    """Constructs JSON POST data for test_hyperglass function"""
    constructed_query = json.dumps(
        {"type": test_query, "location": location, "target": test_target}
    )
    return constructed_query


def flask_dev_server(host, port):
    """Starts Flask development server for testing without WSGI/Reverse Proxy"""
    try:
        sys.path.insert(0, parent_directory)

        from hyperglass import hyperglass
        from hyperglass import configuration
        from hyperglass import render

        render.css()
        logger.info("Starting Flask development server")
        hyperglass.app.run(host=host, debug=True, port=port)
    except:
        logger.error("Exception occurred while trying to start test server...")
        raise


if __name__ == "__main__":
    if ci_config():
        flask_dev_server("localhost", 5000)
    else:
        raise
