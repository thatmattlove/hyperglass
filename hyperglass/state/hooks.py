"""Hooks for accessing hyperglass global state."""

# Standard Library
import typing as t
from functools import lru_cache

# Project
from hyperglass.exceptions.private import StateError

# Local
from .store import HyperglassState
from ..settings import Settings

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.ui import UIParameters
    from hyperglass.models.directive import Directives
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices

    # Local
    from .redis import RedisManager


@lru_cache
def _use_state(attr: t.Optional[str] = None) -> "HyperglassState":
    """Get hyperglass state by property.

    Implemented separately due to typing issues related to lru_cache described here:
    https://github.com/python/mypy/issues/8356
    https://github.com/python/mypy/issues/9112
    """
    if attr is None:
        return HyperglassState(settings=Settings)
    if attr in ("cache", "redis"):
        return HyperglassState(settings=Settings).cache
    if attr in HyperglassState.properties():
        return getattr(HyperglassState(settings=Settings), attr)
    raise StateError("'{attr}' does not exist on HyperglassState", attr=attr)


@t.overload
def use_state(attr: t.Literal["params"]) -> "Params":
    """Access hyperglass configuration parameters from global state."""


@t.overload
def use_state(attr: t.Literal["devices"]) -> "Devices":
    """Access hyperglass devices from global state."""


@t.overload
def use_state(attr: t.Literal["ui_params"]) -> "UIParameters":
    """Access hyperglass UI parameters from global state."""


@t.overload
def use_state(attr: t.Literal["cache", "redis"]) -> "RedisManager":
    """Directly access hyperglass Redis cache manager."""


@t.overload
def use_state(attr: t.Literal["directives"]) -> "Directives":
    """Access all hyperglass directives."""


@t.overload
def use_state(attr=None) -> "HyperglassState":
    """Access entire global state.

    This overload needs to be defined last since it's a catchall.
    """


def use_state(attr: t.Optional[str] = None) -> "HyperglassState":
    """Access global hyperglass state."""
    return _use_state(attr)
