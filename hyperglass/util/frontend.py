"""Utility functions for frontend-related tasks."""

# Standard Library
import shutil
import subprocess


def get_node_version() -> int:
    """Get the system's NodeJS version."""
    node_path = shutil.which("node")

    raw_version = subprocess.check_output(  # noqa: S603
        [node_path, "--version"]
    ).decode()

    # Node returns the version as 'v14.5.0', for example. Remove the v.
    version = raw_version.replace("v", "")
    # Parse the version parts.
    major, minor, patch = version.split(".")

    return int(major)
