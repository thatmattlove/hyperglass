#!/usr/bin/env python3
"""CLI Command definitions."""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
import click

# Project Imports
from cli.echo import cmd_help
from cli.echo import error
from cli.echo import status
from cli.echo import success_info
from cli.echo import value
from cli.formatting import HelpColorsCommand
from cli.formatting import HelpColorsGroup
from cli.formatting import random_colors
from cli.static import CLI_HELP
from cli.static import LABEL
from cli.static import E
from cli.util import fix_ownership
from cli.util import fix_permissions
from cli.util import migrate_config
from cli.util import migrate_systemd
from cli.util import start_web_server

# Define working directory
WORKING_DIR = Path(__file__).parent


@click.group(
    cls=HelpColorsGroup,
    help=CLI_HELP,
    help_headers_color=LABEL,
    help_options_custom_colors=random_colors(
        "build-ui", "start", "migrate-examples", "systemd", "permissions", "secret"
    ),
)
def hg():
    """Initialize Click Command Group."""
    pass


@hg.command("build-ui", short_help=cmd_help(E.BUTTERFLY, "Create a new UI build"))
def build_ui():
    """Create a new UI build.

    Raises:
        click.ClickException: Raised on any errors.
    """
    try:
        import asyncio
        from hyperglass.util import build_ui
    except ImportError as e:
        error("Error importing UI builder", e)

    status("Starting new UI build...")

    try:
        success = asyncio.run(build_ui())
        success_info("Completed build, ran", success)
    except Exception as e:
        error("Error building UI", e)


@hg.command(
    "start",
    help=cmd_help(E.ROCKET, "Start web server"),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-b"),
)
@click.option(
    "-b", "--build", is_flag=True, help="Render theme & build frontend assets"
)
def start(build):
    """Start web server and optionally build frontend assets."""
    try:
        from hyperglass.api import start, ASGI_PARAMS
    except ImportError as e:
        error("Error importing hyperglass", e)

    if build:
        build_complete = build_ui()

        if build_complete:
            start_web_server(start, ASGI_PARAMS)

    if not build:
        start_web_server(start, ASGI_PARAMS)


@hg.command(
    "migrate-examples",
    short_help=cmd_help(E.PAPERCLIP, "Copy example configs to production config files"),
    help=cmd_help(E.PAPERCLIP, "Copy example configs to production config files"),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors(),
)
def migrateconfig():
    """Copy example configuration files to usable config files."""
    migrate_config(WORKING_DIR / "hyperglas/configuration/")


@hg.command(
    "systemd",
    help=cmd_help(E.CLAMP, "Copy systemd example to file system"),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-d"),
)
@click.option(
    "-d",
    "--directory",
    default="/etc/systemd/system",
    help="Destination Directory [default: 'etc/systemd/system']",
)
def migratesystemd(directory):
    """Copy example systemd service file to /etc/systemd/system/."""
    migrate_systemd(WORKING_DIR / "hyperglass/hyperglass.service.example", directory)


@hg.command(
    "permissions",
    help=cmd_help(E.KEY, "Fix ownership & permissions of 'hyperglass/'"),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("--user", "--group"),
)
@click.option("--user", default="www-data")
@click.option("--group", default="www-data")
def permissions(user, group):
    """Run `chmod` and `chown` on the hyperglass/hyperglass directory."""
    fix_permissions(user, group, WORKING_DIR)
    fix_ownership(WORKING_DIR)


@hg.command(
    "secret",
    help=cmd_help(E.LOCK, "Generate agent secret"),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-l"),
)
@click.option(
    "-l", "--length", "length", default=32, help="Number of characters [default: 32]"
)
def generate_secret(length):
    """Generate secret for hyperglass-agent.

    Arguments:
        length {int} -- Length of secret
    """
    import secrets

    gen_secret = secrets.token_urlsafe(length)
    value("Secret", gen_secret)
