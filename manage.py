#!/usr/bin/env python3
import os
import sys
import click
import random
import string
from logzero import logger
from passlib.hash import pbkdf2_sha256

from hyperglass import render as render
from hyperglass import hyperglass


@click.group()
def main():
    pass


@main.command()
def clearcache():
    try:
        hyperglass.clearCache()
        logger.info("Successfully cleared cache.")
    except:
        raise
        logger.error("Failed to clear cache.")


@main.command()
def generatekey(string_length=16):
    ld = string.ascii_letters + string.digits
    api_key = "".join(random.choice(ld) for i in range(string_length))
    key_hash = pbkdf2_sha256.hash(api_key)
    click.echo(
        """
Your API Key is: {api_key}
Place your API Key in the `configuration.py` of your API module. For example, in: `hyperglass-frr/configuration.py`

Your Key Hash is: {key_hash}
Use this hash as the password for the device using the API module. For example, in: `hyperglass/hyperglass/configuration/devices.toml`
""".format(
            api_key=api_key, key_hash=key_hash
        )
    )


@main.command()
def testserver():
    try:
        hyperglass.render.css.renderTemplate()
        hyperglass.app.run(host="0.0.0.0", debug=True, port=5000)
        logger.error("Started test server.")
    except:
        logger.error("Failed to start test server.")
        raise


@main.command()
def render():
    try:
        hyperglass.render.css.renderTemplate()
        logger.info("Successfully rendered CSS templates.")
    except:
        raise
        logger.error("Failed to render CSS templates.")
    try:
        hyperglass.render.html.renderTemplate("index")
        logger.info("Successfully rendered HTML templates.")
    except:
        raise
        logger.error("Failed to render HTML templates.")


if __name__ == "__main__":
    main()
