"""CLI utility functions."""

# Standard Library
import sys
import asyncio

# Third Party
import typer

# Local
from .echo import echo


def build_ui(timeout: int) -> None:
    """Create a new UI build."""
    # Project
    from hyperglass.state import use_state
    from hyperglass.frontend import build_frontend
    from hyperglass.configuration import init_user_config

    # Populate configuration to Redis prior to accessing it.
    init_user_config()

    state = use_state()

    dev_mode = "production"
    if state.settings.dev_mode:
        dev_mode = "development"

    try:
        build_success = asyncio.run(
            build_frontend(
                app_path=state.settings.app_path,
                dev_mode=state.settings.dev_mode,
                dev_url=f"http://localhost:{state.settings.port!s}/",
                force=True,
                params=state.ui_params,
                prod_url="/api/",
                timeout=timeout,
            )
        )
        if build_success:
            echo.success("Completed UI build in {} mode", dev_mode)

    except Exception as e:
        if not sys.stdout.isatty():
            echo._console.print_exception(show_locals=True)
            raise typer.Exit(1)

        echo.error("Error building UI: {!s}", e)
        raise typer.Exit(1)
