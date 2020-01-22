"""Utility fuctions."""


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


def check_python():
    """Verify Python Version.

    Raises:
        RuntimeError: Raised if running Python version is invalid.

    Returns:
        {str} -- Python version
    """
    import sys
    from hyperglass.constants import MIN_PYTHON_VERSION

    pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
    if sys.version_info < MIN_PYTHON_VERSION:
        raise RuntimeError(f"Python {pretty_version}+ is required.")
    return pretty_version


async def build_ui():
    """Execute `yarn build` from UI directory.

    Raises:
        RuntimeError: Raised if exit code is not 0.
        RuntimeError: Raised when any other error occurs.
    """
    import asyncio
    from pathlib import Path

    ui_dir = Path(__file__).parent.parent / "ui"

    yarn_command = "yarn --silent --emoji false --no-progress build"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=yarn_command,
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
    except Exception as e:
        raise RuntimeError(str(e))

    return messages


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


async def build_frontend(dev_mode, dev_url, prod_url, params, force=False):
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

    env_file = Path("/tmp/hyperglass.env.json")  # noqa: S108

    env_vars = {"_HYPERGLASS_CONFIG_": params}
    # Set NextJS production/development mode and base URL based on
    # developer_mode setting.
    if dev_mode:
        env_vars.update({"NODE_ENV": "development", "_HYPERGLASS_URL_": dev_url})
    else:
        env_vars.update({"NODE_ENV": "production", "_HYPERGLASS_URL_": prod_url})

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

                if ef_id == build_id:
                    log.debug(
                        "No changes to UI parameters since last build, skipping..."
                    )
                    return True

        # Create temporary file. .json file extension is added for easy
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
                    build_result = await build_ui()

                    if build_result:
                        log.debug("Completed UI build")
                elif dev_mode and not force:
                    log.debug("Running in developer mode, did not run `yarn build`")

    except Exception as e:
        raise RuntimeError(str(e))

    return True
