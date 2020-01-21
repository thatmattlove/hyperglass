"""Helper functions for CLI message printing."""
# Third Party Imports
import click

# Project Imports
from cli.static import CL
from cli.static import CMD_HELP
from cli.static import ERROR
from cli.static import INFO
from cli.static import LABEL
from cli.static import NL
from cli.static import STATUS
from cli.static import SUCCESS
from cli.static import VALUE
from cli.static import WS
from cli.static import E


def cmd_help(emoji="", help_text=""):
    """Print formatted command help."""
    return emoji + click.style(help_text, **CMD_HELP)


def success(msg):
    """Print formatted success messages."""
    click.echo(E.CHECK + click.style(str(msg), **SUCCESS))


def success_info(label, msg):
    """Print formatted labeled success messages."""
    click.echo(
        E.CHECK
        + click.style(str(label), **SUCCESS)
        + CL[1]
        + WS[1]
        + click.style(str(msg), **INFO)
    )


def info(msg):
    """Print formatted informational messages."""
    click.echo(E.INFO + click.style(str(msg), **INFO))


def status(msg):
    """Print formatted status messages."""
    click.echo(click.style(str(msg), **STATUS))


def error(msg, exc):
    """Raise click exception with formatted output."""
    raise click.ClickException(
        NL
        + E.ERROR
        + click.style(str(msg), **LABEL)
        + CL[1]
        + WS[1]
        + click.style(str(exc), **ERROR)
    ) from None


def value(label, msg):
    """Print formatted label: value."""
    click.echo(
        NL[1]
        + click.style(str(label), **LABEL)
        + CL[1]
        + WS[1]
        + click.style(str(msg), **VALUE)
        + NL[1]
    )
