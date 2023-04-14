"""Utility functions for gathering system information."""

# Standard Library
import os
import sys
import typing as t
import platform

# Third Party
import psutil as _psutil
from cpuinfo import get_cpu_info as _get_cpu_info  # type: ignore

# Project
from hyperglass.constants import __version__

SystemData = t.Dict[str, t.Tuple[t.Union[str, int], str]]


def _cpu() -> SystemData:
    """Construct CPU Information."""
    cpu_info = _get_cpu_info()
    brand = cpu_info.get("brand_raw", "")
    cores_logical = _psutil.cpu_count()
    cores_raw = _psutil.cpu_count(logical=False)
    # TODO: this is currently broken for M1 Macs, check status of: https://github.com/giampaolo/psutil/issues/1892
    cpu_ghz = _psutil.cpu_freq().current / 1000
    return (brand, cores_logical, cores_raw, cpu_ghz)


def _memory() -> SystemData:
    """Construct RAM Information."""
    mem_info = _psutil.virtual_memory()
    total_gb = round(mem_info.total / 1e9, 2)
    usage_percent = mem_info.percent
    return (total_gb, usage_percent)


def _disk() -> SystemData:
    """Construct Disk Information."""
    disk_info = _psutil.disk_usage("/")
    total_gb = round(disk_info.total / 1e9, 2)
    usage_percent = disk_info.percent
    return (total_gb, usage_percent)


def get_node_version() -> t.Tuple[int, int, int]:
    """Get the system's NodeJS version."""

    # Standard Library
    import shutil
    import subprocess

    node_path = shutil.which("node")

    raw_version = subprocess.check_output([node_path, "--version"]).decode()  # noqa: S603

    # Node returns the version as 'v14.5.0', for example. Remove the v.
    version = raw_version.replace("v", "")
    # Parse the version parts.
    return tuple((int(v) for v in version.split(".")))


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
    running_version = ".".join(
        str(v) for v in (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    )
    if sys.version_info < MIN_PYTHON_VERSION:
        raise RuntimeError(f"Python {pretty_version}+ is required (Running {running_version})")
    return running_version


def get_system_info() -> SystemData:
    """Get system info."""

    cpu_info, cpu_logical, cpu_physical, cpu_speed = _cpu()
    mem_total, mem_usage = _memory()
    disk_total, disk_usage = _disk()

    return {
        "hyperglass Version": (__version__, "text"),
        "hyperglass Path": (os.environ["hyperglass_directory"], "code"),
        "Python Version": (platform.python_version(), "code"),
        "Node Version": (".".join(str(v) for v in get_node_version()), "code"),
        "Platform Info": (platform.platform(), "code"),
        "CPU Info": (cpu_info, "text"),
        "Logical Cores": (cpu_logical, "code"),
        "Physical Cores": (cpu_physical, "code"),
        "Processor Speed": (f"{cpu_speed}GHz", "code"),
        "Total Memory": (f"{mem_total} GB", "text"),
        "Memory Utilization": (f"{mem_usage}%", "text"),
        "Total Disk Space": (f"{disk_total} GB", "text"),
        "Disk Utilization": (f"{disk_usage}%", "text"),
    }
