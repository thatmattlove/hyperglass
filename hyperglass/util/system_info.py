"""Utility functions for gathering system information."""

# Standard Library
import os
import platform

# Third Party
import psutil as _psutil
from cpuinfo import get_cpu_info as _get_cpu_info

# Project
from hyperglass.constants import __version__


def _cpu():
    """Construct CPU Information."""
    cpu_info = _get_cpu_info()
    brand = cpu_info.get("brand_raw", "")
    cores_logical = _psutil.cpu_count()
    cores_raw = _psutil.cpu_count(logical=False)
    cpu_ghz = _psutil.cpu_freq().current / 1000
    return (brand, cores_logical, cores_raw, cpu_ghz)


def _memory():
    """Construct RAM Information."""
    mem_info = _psutil.virtual_memory()
    total_gb = round(mem_info.total / 1e9, 2)
    usage_percent = mem_info.percent
    return (total_gb, usage_percent)


def _disk():
    """Construct Disk Information."""
    disk_info = _psutil.disk_usage("/")
    total_gb = round(disk_info.total / 1e9, 2)
    usage_percent = disk_info.percent
    return (total_gb, usage_percent)


def get_system_info():
    """Get system info."""
    yield __version__

    yield os.environ["hyperglass_directory"]

    yield platform.python_version()

    yield platform.platform()

    for c in _cpu():
        yield c
    for m in _memory():
        yield m
    for d in _disk():
        yield d
