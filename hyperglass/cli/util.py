"""CLI utility functions."""
# Standard Library
import os
import shutil
from typing import Iterable
from pathlib import Path

# Third Party
from click import echo, style

# Project
from hyperglass.cli.echo import info, error, status, success, warning
from hyperglass.cli.static import CL, NL, WS, E

PROJECT_ROOT = Path(__file__).parent.parent


def async_command(func):
    """Decororator for to make async functions runable from synchronous code."""
    import asyncio
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


def fix_ownership(user, group, directory):
    """Make user & group the owner of the directory."""
    import grp
    import pwd
    import os

    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    try:
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chown(full_path, uid, gid)
            for f in files:
                full_path = os.path.join(root, f)
                os.chown(full_path, uid, gid)
            os.chown(root, uid, gid)
    except Exception as e:
        error("Failed to change '{d}' ownership: {e}", d="hyperglass/", e=e)

    success("Successfully changed '{d}' ownership", d="hyperglass/")


def fix_permissions(directory):
    """Make directory readable by public."""
    import os

    try:
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chmod(full_path, 0o744)
            for f in files:
                full_path = os.path.join(root, f)
                os.chmod(full_path, 0o744)
            os.chmod(root, 0o744)
    except Exception as e:
        error("Failed to change '{d}' ownership: {e}", d="hyperglass/", e=e)

    success("Successfully changed '{d}' ownership", d="hyperglass/")


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


def migrate_config(config_dir):
    """Copy example config files and remove .example extensions."""
    status("Migrating example config files...")

    import shutil

    examples = Path(PROJECT_ROOT / "examples").glob("*.yaml.example")

    if not isinstance(config_dir, Path):
        config_dir = Path(config_dir)

    if not config_dir.exists():
        error("'{d}' does not exist", d=str(config_dir))

    migrated = 0
    for file in examples:
        target_file = config_dir / file.with_suffix("").name
        try:
            if target_file.exists():
                info("{f} already exists", f=str(target_file))
            else:
                shutil.copyfile(file, target_file)
                migrated += 1
                info("Migrated {f}", f=str(target_file))
        except Exception as e:
            error("Failed to migrate '{f}': {e}", f=str(target_file), e=e)

    if migrated == 0:
        info("Migrated {n} example config files", n=migrated)
    elif migrated > 0:
        success("Successfully migrated {n} example config files", n=migrated)


def migrate_systemd(source, destination):
    """Copy example systemd service file to /etc/systemd/system/."""
    import os
    import shutil

    basefile, extension = os.path.splitext(source)
    newfile = os.path.join(destination, basefile)

    try:
        status("Migrating example systemd service...")

        if os.path.exists(newfile):
            info("'{f}' already exists", f=str(newfile))
        else:
            shutil.copyfile(source, newfile)

    except Exception as e:
        error("Error migrating example systemd service: {e}", e=e)

    success("Successfully migrated systemd service to: {f}", f=str(newfile))


def build_ui():
    """Create a new UI build.

    Raises:
        ClickException: Raised on any errors.
    """
    try:
        from hyperglass.compat._asyncio import aiorun
        from hyperglass.util import build_frontend
        from hyperglass.configuration import params, frontend_params, CONFIG_PATH
    except ImportError as e:
        error("Error importing UI builder: {e}", e=e)

    status("Starting new UI build...")

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


def create_dir(path, **kwargs):
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


def move_files(src, dst, files):  # noqa: C901
    """Move iterable of files from source to destination.

    Arguments:
        src {Path} -- Current directory of files
        dst {Path} -- Target destination directory
        files {Iterable} -- Iterable of files
    """

    if not isinstance(src, Path):
        try:
            src = Path(src)
        except TypeError:
            error("{p} is not a valid path", p=src)
    if not isinstance(dst, Path):
        try:
            dst = Path(dst)
        except TypeError:
            error("{p} is not a valid path", p=dst)

    if not isinstance(files, Iterable):
        error(
            "{fa} must be an iterable (list, tuple, or generator). Received {f}",
            fa="Files argument",
            f=files,
        )

    for path in (src, dst):
        if not path.exists():
            error("{p} does not exist", p=str(path))

    migrated = 0

    for file in files:
        dst_file = dst / file.name

        if not file.exists():
            error("{f} does not exist", f=file)

        try:
            if dst_file.exists():
                warning("{f} already exists", f=dst_file)
            else:
                shutil.copyfile(file, dst_file)
                migrated += 1
                info("Migrated {f}", f=dst_file)
        except Exception as e:
            error("Failed to migrate {f}: {e}", f=dst_file, e=e)

    if migrated == 0:
        warning("Migrated {n} files", n=migrated)
    elif migrated > 0:
        success("Successfully migrated {n} files", n=migrated)
    return True


def make_systemd(user):
    """Generate a systemd file based on the local system.

    Arguments:
        user {str} -- User hyperglass needs to be run as

    Returns:
        {str} -- Generated systemd template
    """

    import platform

    template = """
[Unit]
Description=hyperglass
After=network.target
Requires={redis_name}

[Service]
User={user}
Group={group}
ExecStart={hyperglass_path} start

[Install]
WantedBy=multi-user.target
    """
    known_rhel = ("rhel", "centos")
    distro = platform.linux_distribution()
    if distro[0] in known_rhel:
        redis_name = "redis"
    else:
        redis_name = "redis-server"

    hyperglass_path = shutil.which("hyperglass")

    if not hyperglass_path:
        hyperglass_path = "python3 -m hyperglass.console"
        warning("hyperglass executable not found, using {h}", h=hyperglass_path)

    systemd = template.format(
        redis_name=redis_name, user=user, group=user, hyperglass_path=hyperglass_path
    )
    info(f"Generated systemd service:\n{systemd}")
    return systemd


def write_to_file(file, data):
    """Write string data to a file.

    Arguments:
        file {Path} -- File path
        data {str} -- String data to write

    Returns:
        {bool} -- True if successful
    """
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


def migrate_static_assets(app_path):
    """Migrate app's static assets to app_path.

    Arguments:
        app_path {Path} -- hyperglass runtime path
    """
    from hyperglass.util import migrate_static_assets as _migrate

    migrated, msg, a, b = _migrate(app_path)
    if not migrated:
        callback = error
    elif migrated:
        callback = success

    callback(msg, a=a, b=b)


def install_systemd(app_path):
    """Installs generated systemd file to system's systemd directory.

    Arguments:
        app_path {Path} -- hyperglass runtime path

    Raises:
        ClickException: Raised if the /etc/systemd/system does not exist
        ClickException: Raised if the symlinked file does not exit

    Returns:
        {bool} -- True if successful
    """
    service = app_path / "hyperglass.service"
    systemd = Path("/etc/systemd/system")
    installed = systemd / "hyperglass.service"

    if not systemd.exists():
        error("{e} does not exist. Unable to install systemd service.", e=systemd)

    installed.symlink_to(service)

    if not installed.exists():
        error("Unable to symlink {s} to {d}", s=service, d=installed)

    success("Symlinked {s} to {d}", s=service, d=installed)
    return True
