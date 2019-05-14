#!/usr/bin/env python3
import os
import sys
import click
from logzero import logger
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
