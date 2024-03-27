"""hyperglass state dependencies."""

# Standard Library
import typing as t

# Project
from hyperglass.state import use_state


async def get_state(attr: t.Optional[str] = None):
    """Get hyperglass state as a FastAPI dependency."""
    return use_state(attr)


async def get_params():
    """Get hyperglass params as FastAPI dependency."""
    return use_state("params")


async def get_devices():
    """Get hyperglass devices as FastAPI dependency."""
    return use_state("devices")


async def get_ui_params():
    """Get hyperglass ui_params as FastAPI dependency."""
    return use_state("ui_params")
