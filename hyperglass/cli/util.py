"""CLI utility functions."""

# Standard Library
import os
from pathlib import Path

# Third Party
from click import echo, style

# Project
from hyperglass.cli.echo import info, error, status, success
from hyperglass.cli.static import CL, NL, WS, E

PROJECT_ROOT = Path(__file__).parent.parent


def async_command(func) -> None:
    """Decororator for to make async functions runable from synchronous code."""
    # Standard Library
    import asyncio
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


def start_web_server(start, params):
    """Start web server."""
    msg_start = "Starting hyperglass web server on"
    msg_uri = "http://"
    msg_host = str(params["host"])
    msg_port = str(params["port"])
    msg_len = len("".join([msg_start, WS[1], msg_uri, msg_host, CL[1], msg_port]))
    try:
        echo(
            NL[1]
            + WS[msg_len + 8]
            + E.ROCKET
            + NL[1]
            + E.CHECK
            + style(msg_start, fg="green", bold=True)
            + WS[1]
            + style(msg_uri, fg="white")
            + style(msg_host, fg="blue", bold=True)
            + style(CL[1], fg="white")
            + style(msg_port, fg="magenta", bold=True)
            + WS[1]
            + E.ROCKET
            + NL[1]
            + WS[1]
            + NL[1]
        )
        start()

    except Exception as e:
        error("Failed to start web server: {e}", e=e)


def build_ui(timeout: int) -> None:
    """Create a new UI build."""
    try:
        # Project
        from hyperglass.configuration import CONFIG_PATH, params, frontend_params
        from hyperglass.util.frontend import build_frontend
        from hyperglass.compat._asyncio import aiorun
    except ImportError as e:
        error("Error importing UI builder: {e}", e=e)

    status("Starting new UI build with a {t} second timeout...", t=timeout)

    if params.developer_mode:
        dev_mode = "development"
    else:
        dev_mode = "production"

    try:
        build_success = aiorun(
            build_frontend(
                dev_mode=params.developer_mode,
                dev_url=f"http://localhost:{str(params.listen_port)}/",
                prod_url="/api/",
                params=frontend_params,
                force=True,
                app_path=CONFIG_PATH,
            )
        )
        if build_success:
            success("Completed UI build in {m} mode", m=dev_mode)

    except Exception as e:
        error("Error building UI: {e}", e=e)

    return True


def create_dir(path, **kwargs) -> bool:
    """Validate and attempt to create a directory, if it does not exist."""

    # If input path is not a path object, try to make it one
    if not isinstance(path, Path):
        try:
            path = Path(path)
        except TypeError:
            error("{p} is not a valid path", p=path)

    # If path does not exist, try to create it
    if not path.exists():
        try:
            path.mkdir(**kwargs)
        except PermissionError:
            error(
                "{u} does not have permission to create {p}. Try running with sudo?",
                u=os.getlogin(),
                p=path,
            )

        # Verify the path was actually created
        if path.exists():
            success("Created {p}", p=path)

    # If the path already exists, inform the user
    elif path.exists():
        info("{p} already exists", p=path)

    return True


def write_to_file(file, data) -> bool:
    """Write string data to a file."""
    try:
        with file.open("w+") as f:
            f.write(data.strip())
    except PermissionError:
        error(
            "{u} does not have permission to write to {f}. Try running with sudo?",
            u=os.getlogin(),
            f=file,
        )
    if not file.exists():
        error("Error writing file {f}", f=file)
    elif file.exists():
        success("Wrote systemd file {f}", f=file)
    return True


def system_info() -> bool:
    """Create a markdown table of various system information."""
    # Project
    from hyperglass.util.system_info import get_system_info

    values = get_system_info()

    def _code(val):
        return f"`{str(val)}`"

    def _bold(val):
        return f"**{str(val)}**"

    def _suffix(val, suffix):
        return f"{str(val)}{str(suffix)}"

    columns = (
        ("hyperglass Version", _bold),
        ("hyperglass Path", _code),
        ("Python Version", _code),
        ("Platform Info", _code),
        ("CPU Info", None),
        ("Logical Cores", _code),
        ("Physical Cores", _code),
        ("Processor Speed", "GHz"),
        ("Total Memory", " GB"),
        ("Memory Utilization", "%"),
        ("Total Disk Space", " GB"),
        ("Disk Utilization", "%"),
    )
    md_table_lines = ("| Metric | Value |", "| ------ | ----- |")

    for i, metric in enumerate(values):
        title, mod = columns[i]
        value = metric

        if isinstance(mod, str):
            value = _suffix(value, mod)
        elif callable(mod):
            value = mod(value)

        md_table_lines += (f"| **{title}** | {value} |",)

    md_table = "\n".join(md_table_lines)

    info("Please copy & paste this table in your bug report:\n")
    echo(md_table + "\n")

    return True
