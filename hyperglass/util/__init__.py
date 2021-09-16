"""Utility functions."""

# Standard Library
import os
import sys
import json
import string
import typing as t
import platform
from asyncio import iscoroutine
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address, ip_address

# Third Party
from loguru._logger import Logger as LoguruLogger
from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

# Project
from hyperglass.log import log
from hyperglass.constants import DRIVER_MAP

ALL_DEVICE_TYPES = {*DRIVER_MAP.keys(), *CLASS_MAPPER.keys()}
ALL_DRIVERS = {*DRIVER_MAP.values(), "netmiko"}

DeepConvert = t.TypeVar("DeepConvert", bound=t.Dict[str, t.Any])


def cpu_count(multiplier: int = 0) -> int:
    """Get server's CPU core count.

    Used to determine the number of web server workers.
    """
    # Standard Library
    import multiprocessing

    return multiprocessing.cpu_count() * multiplier


def check_python() -> str:
    """Verify Python Version."""
    # Project
    from hyperglass.constants import MIN_PYTHON_VERSION

    pretty_version = ".".join(tuple(str(v) for v in MIN_PYTHON_VERSION))
    if sys.version_info < MIN_PYTHON_VERSION:
        raise RuntimeError(f"Python {pretty_version}+ is required.")
    return platform.python_version()


async def write_env(variables: t.Dict) -> str:
    """Write environment variables to temporary JSON file."""
    env_file = Path("/tmp/hyperglass.env.json")  # noqa: S108
    env_vars = json.dumps(variables)

    try:
        with env_file.open("w+") as ef:
            ef.write(env_vars)
    except Exception as e:
        raise RuntimeError(str(e))

    return f"Wrote {env_vars} to {str(env_file)}"


def set_app_path(required: bool = False) -> Path:
    """Find app directory and set value to environment variable."""

    # Standard Library
    from getpass import getuser

    matched_path = None

    config_paths = (Path.home() / "hyperglass", Path("/etc/hyperglass/"))

    # Ensure only one app directory exists to reduce confusion.
    if all((p.exists() for p in config_paths)):
        raise RuntimeError(
            "Both '{}' and '{}' exist. ".format(*(p.as_posix() for p in config_paths))
            + "Please choose only one configuration directory and delete the other."
        )

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
                dir="\n".join(["\t - " + str(p) for p in config_paths]),
            )
        )

    os.environ["hyperglass_directory"] = str(matched_path)
    return matched_path


def split_on_uppercase(s):
    """Split characters by uppercase letters.

    From: https://stackoverflow.com/a/40382663
    """
    string_length = len(s)
    is_lower_around = lambda: s[i - 1].islower() or string_length > (i + 1) and s[i + 1].islower()

    start = 0
    parts = []
    for i in range(1, string_length):
        if s[i].isupper() and is_lower_around():
            parts.append(s[start:i])
            start = i
    parts.append(s[start:])

    return parts


def parse_exception(exc):
    """Parse an exception and its direct cause."""

    if not isinstance(exc, BaseException):
        raise TypeError(f"'{repr(exc)}' is not an exception.")

    def get_exc_name(exc):
        return " ".join(split_on_uppercase(exc.__class__.__name__))

    def get_doc_summary(doc):
        return doc.strip().split("\n")[0].strip(".")

    name = get_exc_name(exc)
    parsed = []
    if exc.__doc__:
        detail = get_doc_summary(exc.__doc__)
        parsed.append(f"{name} ({detail})")
    else:
        parsed.append(name)

    if exc.__cause__:
        cause = get_exc_name(exc.__cause__)
        if exc.__cause__.__doc__:
            cause_detail = get_doc_summary(exc.__cause__.__doc__)
            parsed.append(f"{cause} ({cause_detail})")
        else:
            parsed.append(cause)
    return ", caused by ".join(parsed)


def set_cache_env(host, port, db):
    """Set basic cache config parameters to environment variables.

    Functions using Redis to access the pickled config need to be able
    to access Redis without reading the config.
    """

    os.environ["HYPERGLASS_CACHE_HOST"] = str(host)
    os.environ["HYPERGLASS_CACHE_PORT"] = str(port)
    os.environ["HYPERGLASS_CACHE_DB"] = str(db)
    return True


def get_cache_env():
    """Get basic cache config from environment variables."""

    host = os.environ.get("HYPERGLASS_CACHE_HOST")
    port = os.environ.get("HYPERGLASS_CACHE_PORT")
    db = os.environ.get("HYPERGLASS_CACHE_DB")
    for i in (host, port, db):
        if i is None:
            raise LookupError("Unable to find cache configuration in environment variables")
    return host, port, db


def make_repr(_class):
    """Create a user-friendly represention of an object."""

    def _process_attrs(_dir):
        for attr in _dir:
            if not attr.startswith("_"):
                attr_val = getattr(_class, attr)

                if callable(attr_val):
                    yield f'{attr}=<function name="{attr_val.__name__}">'

                elif iscoroutine(attr_val):
                    yield f'{attr}=<coroutine name="{attr_val.__name__}">'

                elif isinstance(attr_val, str):
                    yield f'{attr}="{attr_val}"'

                else:
                    yield f"{attr}={str(attr_val)}"

    return f'{_class.__name__}({", ".join(_process_attrs(dir(_class)))})'


def validate_device_type(_type: str) -> t.Tuple[bool, t.Union[None, str]]:
    """Validate device type is supported."""

    result = (False, None)

    if _type in ALL_DEVICE_TYPES:
        result = (True, DRIVER_MAP.get(_type, "netmiko"))

    return result


def get_driver(_type: str, driver: t.Optional[str]) -> str:
    """Determine the appropriate driver for a device."""

    if driver is None:
        # If no driver is set, use the driver map with netmiko as
        # fallback.
        return DRIVER_MAP.get(_type, "netmiko")
    elif driver in ALL_DRIVERS:
        # If a driver is set and it is valid, allow it.
        return driver
    else:
        # Otherwise, fail validation.
        raise ValueError("{} is not a supported driver.".format(driver))


def current_log_level(logger: LoguruLogger) -> str:
    """Get the current log level of a logger instance."""

    try:
        handler = list(logger._core.handlers.values())[0]
        levels = {v.no: k for k, v in logger._core.levels.items()}
        current_level = levels[handler.levelno].lower()

    except Exception as err:
        logger.error(err)
        current_level = "info"

    return current_level


def resolve_hostname(hostname: str) -> t.Generator[t.Union[IPv4Address, IPv6Address], None, None]:
    """Resolve a hostname via DNS/hostfile."""
    # Standard Library
    from socket import gaierror, getaddrinfo

    log.debug("Ensuring '{}' is resolvable...", hostname)

    ip4 = None
    ip6 = None
    try:
        res = getaddrinfo(hostname, None)
        for sock in res:
            if sock[0].value == 2 and ip4 is None:
                ip4 = ip_address(sock[4][0])
            elif sock[0].value in (10, 30) and ip6 is None:
                ip6 = ip_address(sock[4][0])
    except (gaierror, ValueError, IndexError) as err:
        log.debug(str(err))
        pass

    yield ip4
    yield ip6


def snake_to_camel(value: str) -> str:
    """Convert a string from snake_case to camelCase."""
    parts = value.split("_")
    humps = (hump.capitalize() for hump in parts[1:])
    return "".join((parts[0], *humps))


def get_fmt_keys(template: str) -> t.List[str]:
    """Get a list of str.format keys.

    For example, string `"The value of {key} is {value}"` returns
    `["key", "value"]`.
    """
    keys = []
    for block in (b for b in string.Formatter.parse("", template) if isinstance(template, str)):
        key = block[1]
        if key:
            keys.append(key)
    return keys


def deep_convert_keys(_dict: t.Type[DeepConvert], predicate: t.Callable[[str], str]) -> DeepConvert:
    """Convert all dictionary keys and nested dictionary keys."""
    converted = {}

    def get_value(value: t.Any):
        if isinstance(value, t.Dict):
            return {predicate(k): get_value(v) for k, v in value.items()}
        elif isinstance(value, t.List):
            return [get_value(v) for v in value]
        elif isinstance(value, t.Tuple):
            return tuple(get_value(v) for v in value)
        return value

    for key, value in _dict.items():
        converted[predicate(key)] = get_value(value)

    return converted


def at_least(minimum: int, value: int,) -> int:
    """Get a number value that is at least a specified minimum."""
    if value < minimum:
        return minimum
    return value
