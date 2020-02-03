#!/usr/bin/env python3
"""CLI Command definitions."""

# Standard Library
from pathlib import Path

# Third Party
import click

# Project
from cli.echo import error, value, cmd_help
from cli.util import (
    build_ui,
    fix_ownership,
    migrate_config,
    fix_permissions,
    migrate_systemd,
    start_web_server,
)
from cli.static import LABEL, CLI_HELP, E
from cli.formatting import HelpColorsGroup, HelpColorsCommand, random_colors

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


@hg.command("build-ui", help=cmd_help(E.BUTTERFLY, "Create a new UI build"))
def build_frontend():
    """Create a new UI build.

    Raises:
        click.ClickException: Raised on any errors.
    """
    return build_ui()


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
@click.option("-d", "--directory", required=True, help="Target directory")
def migrateconfig(directory):
    """Copy example configuration files to usable config files."""
    migrate_config(Path(directory))


@hg.command(
    "systemd",
    help=cmd_help(E.CLAMP, " Copy systemd example to file system"),
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
