"""CLI Command definitions."""

# Standard Library
import sys
from pathlib import Path

# Third Party
from click import group, option, help_option

# Project
from hyperglass.util import cpu_count

# Local
from .echo import error, label, success, warning, cmd_help
from .util import build_ui
from .static import LABEL, CLI_HELP, E
from .installer import Installer
from .formatting import HelpColorsGroup, HelpColorsCommand, random_colors

# Define working directory
WORKING_DIR = Path(__file__).parent

supports_color = "utf" in sys.getfilesystemencoding().lower()


def _print_version(ctx, param, value):
    # Project
    from hyperglass import __version__

    if not value or ctx.resilient_parsing:
        return
    label("hyperglass version: {v}", v=__version__)
    ctx.exit()


@group(
    cls=HelpColorsGroup,
    help=CLI_HELP,
    context_settings={"help_option_names": ["-h", "--help"], "color": supports_color},
    help_headers_color=LABEL,
    help_options_custom_colors=random_colors(
        "build-ui", "start", "secret", "setup", "system-info", "clear-cache"
    ),
)
@option(
    "-v",
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help=cmd_help(E.NUMBERS, "hyperglass version", supports_color),
)
@help_option(
    "-h",
    "--help",
    help=cmd_help(E.FOLDED_HANDS, "Show this help message", supports_color),
)
def hg():
    """Initialize Click Command Group."""
    pass


@hg.command(
    "build-ui", help=cmd_help(E.BUTTERFLY, "Create a new UI build", supports_color)
)
@option("-t", "--timeout", required=False, default=180, help="Timeout in seconds")
def build_frontend(timeout):
    """Create a new UI build."""
    return build_ui(timeout)


@hg.command(  # noqa: C901
    "start",
    help=cmd_help(E.ROCKET, "Start web server", supports_color),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-b", "-d", "-w"),
)
@option("-b", "--build", is_flag=True, help="Render theme & build frontend assets")
@option(
    "-d",
    "--direct",
    is_flag=True,
    default=False,
    help="Start hyperglass directly instead of through process manager",
)
@option(
    "-w",
    "--workers",
    type=int,
    required=False,
    default=0,
    help=f"Number of workers. By default, calculated from CPU cores [{cpu_count(2)}]",
)
def start(build, direct, workers):  # noqa: C901
    """Start web server and optionally build frontend assets."""
    # Project
    from hyperglass.api import start as uvicorn_start
    from hyperglass.main import start

    kwargs = {}
    if workers != 0:
        kwargs["workers"] = workers

    try:

        if build:
            build_complete = build_ui(timeout=180)

            if build_complete and not direct:
                start(**kwargs)
            elif build_complete and direct:
                uvicorn_start(**kwargs)

        if not build and not direct:
            start(**kwargs)

        elif not build and direct:
            uvicorn_start(**kwargs)

    except (KeyboardInterrupt, SystemExit) as err:
        error_message = str(err)
        if (len(error_message)) > 1:
            warning(str(err))
        error("Stopping hyperglass due to keyboard interrupt.")

    except BaseException as err:
        error(str(err))


@hg.command(
    "secret",
    help=cmd_help(E.LOCK, "Generate agent secret", supports_color),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-l"),
)
@option(
    "-l", "--length", "length", default=32, help="Number of characters [default: 32]"
)
def generate_secret(length):
    """Generate secret for hyperglass-agent.

    Arguments:
        length {int} -- Length of secret
    """
    # Standard Library
    import secrets

    gen_secret = secrets.token_urlsafe(length)
    label("Secret: {s}", s=gen_secret)


@hg.command(
    "setup",
    help=cmd_help(E.TOOLBOX, "Run the setup wizard", supports_color),
    cls=HelpColorsCommand,
    help_options_custom_colors=random_colors("-d"),
)
@option(
    "-d",
    "--use-defaults",
    "unattended",
    default=False,
    is_flag=True,
    help="Use hyperglass defaults (requires no input)",
)
def setup(unattended):
    """Define application directory, move example files, generate systemd service."""

    installer = Installer(unattended=unattended)
    installer.install()

    success(
        """Completed hyperglass installation.
After adding your hyperglass.yaml file, you should run the `hyperglass build-ui` command."""  # noqa: E501
    )


@hg.command(
    "system-info",
    help=cmd_help(
        E.THERMOMETER, "  Get system information for a bug report", supports_color
    ),
    cls=HelpColorsCommand,
)
def get_system_info():
    """Get CPU, Memory, Disk, Python, & hyperglass version."""
    # Project
    from hyperglass.cli.util import system_info

    system_info()


@hg.command(
    "clear-cache",
    help=cmd_help(E.SOAP, "Clear the Redis cache", supports_color),
    cls=HelpColorsCommand,
)
def clear_cache():
    """Clear the Redis Cache."""
    # Project
    from hyperglass.util import sync_clear_redis_cache

    try:
        sync_clear_redis_cache()
        success("Cleared Redis Cache")
    except RuntimeError as err:
        error(str(err))
