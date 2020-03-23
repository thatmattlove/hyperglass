"""Utility functions."""


def _logger():
    from loguru import logger as _loguru_logger
    from hyperglass.constants import LOG_HANDLER
    from hyperglass.constants import LOG_LEVELS

    _loguru_logger.remove()
    _loguru_logger.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)
    return _loguru_logger


log = _logger()


def cpu_count():
    """Get server's CPU core count.

    Used for number of web server workers.

    Returns:
        {int} -- CPU Cores
    """
    import multiprocessing

    return multiprocessing.cpu_count()


def clean_name(_name):
    """Remove unsupported characters from field names.

    Converts any "desirable" seperators to underscore, then removes all
    characters that are unsupported in Python class variable names.
    Also removes leading numbers underscores.

    Arguments:
        _name {str} -- Initial field name

    Returns:
        {str} -- Cleaned field name
    """
    import re

    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


async def check_path(path, mode="r"):
    """Verify if a path exists and is accessible.

    Arguments:
        path {Path|str} -- Path object or string of path
        mode {str} -- File mode, r or w

    Raises:
        RuntimeError: Raised if file does not exist or is not accessible

    Returns:
        {Path|None} -- Path object if checks pass, None if not.
    """
    from pathlib import Path
    from aiofile import AIOFile

    try:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"{str(path)} does not exist.")

        async with AIOFile(path, mode):
            result = path

    except Exception:
        result = None

    return result


def check_python():
    """Verify Python Version.

    Raises:
        RuntimeError: Raised if running Python version is invalid.

    Returns:
        {str} -- Python version
    """
    import sys
    import platform
    from hyperglass.constants import MIN_PYTHON_VERSION

    pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
    if sys.version_info < MIN_PYTHON_VERSION:
        raise RuntimeError(f"Python {pretty_version}+ is required.")
    return platform.python_version()


async def build_ui(app_path):
    """Execute `next build` & `next export` from UI directory.

    Raises:
        RuntimeError: Raised if exit code is not 0.
        RuntimeError: Raised when any other error occurs.
    """
    import asyncio
    from pathlib import Path

    ui_dir = Path(__file__).parent / "ui"
    build_dir = app_path / "static" / "ui"

    build_command = "node_modules/.bin/next build"
    export_command = "node_modules/.bin/next export -o {f}".format(f=build_dir)

    all_messages = []
    for command in (build_command, export_command):
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd=command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ui_dir,
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            messages = stdout.decode("utf-8").strip()
            errors = stderr.decode("utf-8").strip()

            if proc.returncode != 0:
                raise RuntimeError(f"\nMessages:\n{messages}\nErrors:\n{errors}")

            await proc.wait()
            all_messages.append(messages)

        except Exception as e:
            raise RuntimeError(str(e))

    return "\n".join(all_messages)


async def write_env(variables):
    """Write environment variables to temporary JSON file.

    Arguments:
        variables {dict} -- Environment variables to write.

    Raises:
        RuntimeError: Raised on any errors.
    """
    from aiofile import AIOFile
    import ujson as json
    from pathlib import Path

    env_file = Path("/tmp/hyperglass.env.json")  # noqa: S108
    env_vars = json.dumps(variables)

    try:
        async with AIOFile(env_file, "w+") as ef:
            await ef.write(env_vars)
            await ef.fsync()
    except Exception as e:
        raise RuntimeError(str(e))

    return f"Wrote {env_vars} to {str(env_file)}"


async def check_redis(db, config):
    """Ensure Redis is running before starting server.

    Arguments:
        db {int} -- Redis database ID
        config {dict} -- Redis configuration parameters

    Raises:
        RuntimeError: Raised if Redis is not running.

    Returns:
        {bool} -- True if redis is running.
    """
    import aredis

    redis_instance = aredis.StrictRedis(db=db, **config)
    redis_host = config["host"]
    redis_port = config["port"]
    try:
        await redis_instance.echo("hyperglass test")
    except Exception:
        raise RuntimeError(
            f"Redis isn't running at: {redis_host}:{redis_port}"
        ) from None
    return True


async def clear_redis_cache(db, config):
    """Clear the Redis cache.

    Arguments:
        db {int} -- Redis database ID
        config {dict} -- Redis configuration parameters

    Raises:
        RuntimeError: Raised if clearing the cache produces an error.

    Returns:
        {bool} -- True if cache was cleared.
    """
    import aredis

    try:
        redis_instance = aredis.StrictRedis(db=db, **config)
        await redis_instance.flushdb()
    except Exception as e:
        raise RuntimeError(f"Error clearing cache: {str(e)}") from None
    return True


async def move_files(src, dst, files):  # noqa: C901
    """Move iterable of files from source to destination.

    Arguments:
        src {Path} -- Current directory of files
        dst {Path} -- Target destination directory
        files {Iterable} -- Iterable of files
    """
    import shutil
    from pathlib import Path
    from typing import Iterable

    def error(*args, **kwargs):
        msg = ", ".join(args)
        kwargs = {k: str(v) for k, v in kwargs.items()}
        error_msg = msg.format(**kwargs)
        log.error(error_msg)
        return RuntimeError(error_msg)

    if not isinstance(src, Path):
        try:
            src = Path(src)
        except TypeError:
            raise error("{p} is not a valid path", p=src)

    if not isinstance(dst, Path):
        try:
            dst = Path(dst)
        except TypeError:
            raise error("{p} is not a valid path", p=dst)

    if not isinstance(files, Iterable):
        raise error(
            "{fa} must be an iterable (list, tuple, or generator). Received {f}",
            fa="Files argument",
            f=files,
        )

    for path in (src, dst):
        if not path.exists():
            raise error("{p} does not exist", p=path)

    migrated = ()

    for file in files:
        dst_file = dst / file.name

        if not file.exists():
            raise error("{f} does not exist", f=file)

        try:
            if not dst_file.exists():
                shutil.copyfile(file, dst_file)
                migrated += (str(dst_file),)
        except Exception as e:
            raise error("Failed to migrate {f}: {e}", f=dst_file, e=e)

    return migrated


def migrate_static_assets(app_path):
    """Synchronize the project assets with the installation assets."""
    import shutil
    from pathlib import Path
    from filecmp import dircmp

    asset_dir = Path(__file__).parent / "images"
    target_dir = app_path / "static" / "images"

    target_exists = target_dir.exists()

    if not target_exists:
        shutil.copytree(asset_dir, target_dir)

    # Compare the contents of the project's asset directory (considered
    # the source of truth) with the installation directory. If they do
    # not match, delete the installation directory's asset directory and
    # re-copy it.
    compare_initial = dircmp(asset_dir, target_dir, ignore=[".DS_Store"])

    if not compare_initial.left_list == compare_initial.right_list:
        shutil.rmtree(target_dir)
        shutil.copytree(asset_dir, target_dir)

        # Re-compare the source and destination directory contents to
        # ensure they match.
        compare_post = dircmp(asset_dir, target_dir, ignore=[".DS_Store"])

        if not compare_post.left_list == compare_post.right_list:
            return (
                False,
                "Files in {a} do not match files in {b}",
                str(asset_dir),
                str(target_dir),
            )
    return (True, "Migrated assets from {a} to {b}", str(asset_dir), str(target_dir))


async def check_node_modules():
    """Check if node_modules exists and has contents.

    Returns:
        {bool} -- True if exists and has contents.
    """
    from pathlib import Path

    ui_path = Path(__file__).parent / "ui"
    node_modules = ui_path / "node_modules"

    exists = node_modules.exists()
    valid = exists

    if exists and not tuple(node_modules.iterdir()):
        valid = False

    return valid


async def node_initial(dev_mode=False):
    """Initialize node_modules.

    Raises:
        RuntimeError: Raised if exit code is not 0
        RuntimeError: Raised if other exceptions occur

    Returns:
        {str} -- Command output
    """
    import asyncio
    from pathlib import Path

    ui_path = Path(__file__).parent / "ui"

    mode = ""
    if not dev_mode:
        mode = "--prod"

    command = "yarn {m} --silent --emoji false".format(m=mode)

    all_messages = []
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ui_path,
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        messages = stdout.decode("utf-8").strip()
        errors = stderr.decode("utf-8").strip()

        if proc.returncode != 0:
            raise RuntimeError(f"\nMessages:\n{messages}\nErrors:\n{errors}")

        await proc.wait()
        all_messages.append(messages)

    except Exception as e:
        raise RuntimeError(str(e))

    return "\n".join(all_messages)


async def read_package_json():
    """Import package.json as a python dict.

    Raises:
        RuntimeError: Raised if unable to read package.json

    Returns:
        {dict} -- NPM package.json as dict
    """
    from pathlib import Path
    import ujson

    package_json_file = Path(__file__).parent / "ui" / "package.json"

    try:

        with package_json_file.open("r") as file:
            package_json = ujson.load(file)

    except Exception as e:
        raise RuntimeError(f"Error reading package.json: {str(e)}")

    log.debug("package.json:\n{p}", p=package_json)

    return package_json


async def build_frontend(  # noqa: C901
    dev_mode, dev_url, prod_url, params, app_path, force=False
):
    """Perform full frontend UI build process.

    Securely creates temporary file, writes frontend configuration
    parameters to file as JSON. Then writes the name of the temporary
    file to /tmp/hyperglass.env.json as {"configFile": <file_name> }.

    Webpack reads /tmp/hyperglass.env.json, loads the temporary file,
    and sets its contents to Node environment variables during the build
    process.

    After the build is successful, the temporary file is automatically
    closed during garbage collection.

    Arguments:
        dev_mode {bool} -- Development Mode
        dev_url {str} -- Development Mode URL
        prod_url {str} -- Production Mode URL
        params {dict} -- Frontend Config paramters

    Raises:
        RuntimeError: Raised if errors occur during build process.

    Returns:
        {bool} -- True if successful
    """
    import hashlib
    import tempfile
    from pathlib import Path
    from aiofile import AIOFile
    import ujson as json
    from hyperglass.constants import __version__

    env_file = Path("/tmp/hyperglass.env.json")  # noqa: S108

    package_json = await read_package_json()

    env_vars = {
        "_HYPERGLASS_CONFIG_": params,
        "_HYPERGLASS_VERSION_": __version__,
        "_HYPERGLASS_PACKAGE_JSON_": package_json,
    }

    # Set NextJS production/development mode and base URL based on
    # developer_mode setting.
    if dev_mode:
        env_vars.update({"NODE_ENV": "development", "_HYPERGLASS_URL_": dev_url})
    else:
        env_vars.update({"NODE_ENV": "production", "_HYPERGLASS_URL_": prod_url})

    # Check if hyperglass/ui/node_modules has been initialized. If not,
    # initialize it.
    initialized = await check_node_modules()
    if initialized:
        log.debug("node_modules is already initialized")
    elif not initialized:
        log.debug("node_modules has not been initialized. Starting initialization...")
        node_setup = await node_initial(dev_mode)
        if node_setup == "":
            log.debug("Re-initialized node_modules")

    try:
        env_json = json.dumps(env_vars)

        # Create SHA256 hash from all parameters passed to UI, use as
        # build identifier.
        build_id = hashlib.sha256(env_json.encode()).hexdigest()

        # Read hard-coded environment file from last build. If build ID
        # matches this build's ID, don't run a new build.
        if env_file.exists() and not force:
            async with AIOFile(env_file, "r") as ef:
                ef_json = await ef.read()
                ef_id = json.loads(ef_json).get("buildId", "empty")

                log.debug("Previous Build ID: {id}", id=ef_id)

                if ef_id == build_id:
                    log.debug(
                        "UI parameters unchanged since last build, skipping UI build..."
                    )
                    return True

        # Create temporary file. json file extension is added for easy
        # webpack JSON parsing.
        temp_file = tempfile.NamedTemporaryFile(
            mode="w+", prefix="hyperglass_", suffix=".json", delete=not dev_mode
        )
        log.debug(
            f"Created temporary UI config file: '{temp_file.name}' for build {build_id}"
        )

        async with AIOFile(temp_file.name, "w+") as temp:
            await temp.write(env_json)
            await temp.fsync()

            # Write "permanent" file (hard-coded named) for Node to read.
            async with AIOFile(env_file, "w+") as ef:
                await ef.write(
                    json.dumps({"configFile": temp_file.name, "buildId": build_id})
                )
                await ef.fsync()

                # While temporary file is still open, initiate UI build process.
                if not dev_mode or force:
                    initialize_result = await node_initial(dev_mode)
                    build_result = await build_ui(app_path=app_path)

                    if initialize_result:
                        log.debug(initialize_result)
                    elif initialize_result == "":
                        log.debug("Re-initialized node_modules")

                    if build_result:
                        log.debug("Completed UI build")
                elif dev_mode and not force:
                    log.debug("Running in developer mode, did not build new UI files")

        migrate_static_assets(app_path)

    except Exception as e:
        raise RuntimeError(str(e))

    return True


def set_app_path(required=False):
    """Find app directory and set value to environment variable."""
    import os
    from pathlib import Path
    from getpass import getuser

    matched_path = None

    config_paths = (Path.home() / "hyperglass", Path("/etc/hyperglass/"))

    for path in config_paths:
        try:
            if path.exists():
                tmp = path / "test.tmp"
                tmp.touch()
                if tmp.exists():
                    matched_path = path
                    tmp.unlink()
                    break
        except Exception:
            matched_path = None

    if required and matched_path is None:
        # Only raise an error if required is True
        raise RuntimeError(
            """
    No configuration directories were determined to both exist and be readable
    by hyperglass. hyperglass is running as user '{un}' (UID '{uid}'), and tried
    to access the following directories:
    {dir}""".format(
                un=getuser(),
                uid=os.getuid(),
                dir="\n".join([" - " + str(p) for p in config_paths]),
            )
        )

    os.environ["hyperglass_directory"] = str(matched_path)
    return True


def import_public_key(app_path, device_name, keystring):
    """Import a public key for hyperglass-agent.

    Arguments:
        app_path {Path|str} -- hyperglass app path
        device_name {str} -- Device name
        keystring {str} -- Public key

    Raises:
        RuntimeError: Raised if unable to create certs directory
        RuntimeError: Raised if written key does not match input

    Returns:
        {bool} -- True if file was written
    """
    import re
    from pathlib import Path

    if not isinstance(app_path, Path):
        app_path = Path(app_path)

    cert_dir = app_path / "certs"

    if not cert_dir.exists():
        cert_dir.mkdir()

    if not cert_dir.exists():
        raise RuntimeError(f"Failed to create certs directory at {str(cert_dir)}")

    filename = re.sub(r"[^A-Za-z0-9]", "_", device_name) + ".pem"
    cert_file = cert_dir / filename

    with cert_file.open("w+") as file:
        file.write(str(keystring))

    with cert_file.open("r") as file:
        read_file = file.read().strip()
        if not keystring == read_file:
            raise RuntimeError("Wrote key, but written file did not match input key")

    return True
