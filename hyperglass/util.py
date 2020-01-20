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
    import ujson as json

    ui_dir = Path(__file__).parent.parent / "ui"

    yarn_command = "yarn --silent --emoji false --json --no-progress build"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=yarn_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ui_dir,
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        output_out = json.loads(stdout.decode("utf-8").split("\n")[0])

        if proc.returncode != 0:
            output_error = json.loads(stderr.decode("utf-8").strip("\n"))
            raise RuntimeError(
                f'Error building web assets with script {output_out["data"]}:'
                f'{output_error["data"]}'
            )

        await proc.wait()
    except Exception as e:
        raise RuntimeError(str(e))

    return output_out["data"]


async def write_env(vars):
    """Write environment variables to temporary JSON file.

    Arguments:
        vars {dict} -- Environment variables to write.

    Raises:
        RuntimeError: Raised on any errors.
    """
    from aiofile import AIOFile
    import ujson as json
    from pathlib import Path

    env_file = Path("/tmp/hyperglass.env.json")
    env_vars = json.dumps(vars)

    try:
        async with AIOFile(env_file, "w+") as ef:
            await ef.write(env_vars)
            await ef.fsync()
    except Exception as e:
        raise RuntimeError(str(e))

    return True
