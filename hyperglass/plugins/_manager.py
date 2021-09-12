"""Plugin manager definition."""

# Standard Library
import json
import codecs
import pickle
from typing import List, Generic, TypeVar, Callable, Generator
from inspect import isclass

# Project
from hyperglass.log import log
from hyperglass.cache import SyncCache
from hyperglass.configuration import REDIS_CONFIG, params
from hyperglass.exceptions.private import PluginError

# Local
from ._base import PluginType, HyperglassPlugin
from ._input import InputPlugin
from ._output import OutputPlugin

PluginT = TypeVar("PluginT")


class PluginManager(Generic[PluginT]):
    """Manage all plugins."""

    _type: PluginType
    _cache: SyncCache
    _index: int = 0
    _cache_key: str

    def __init__(self: "PluginManager") -> None:
        """Initialize plugin manager."""
        self._cache = SyncCache(db=params.cache.database, **REDIS_CONFIG)
        self._cache_key = f"hyperglass.plugins.{self._type}"

    def __init_subclass__(cls: "PluginManager", **kwargs: PluginType) -> None:
        """Set this plugin manager's type on subclass initialization."""
        _type = kwargs.get("type", None) or cls._type
        if _type is None:
            raise PluginError(
                "Plugin '{}' is missing a 'type', keyword argument", repr(cls)
            )
        cls._type = _type
        return super().__init_subclass__()

    def __iter__(self: "PluginManager") -> "PluginManager":
        """Plugin manager iterator."""
        return self

    def __next__(self: "PluginManager") -> PluginT:
        """Plugin manager iteration."""
        if self._index <= len(self.plugins):
            result = self.plugins[self._index - 1]
            self._index += 1
            return result
        self._index = 0
        raise StopIteration

    def _get_plugins(self: "PluginManager") -> List[PluginT]:
        """Retrieve plugins from cache."""
        cached = self._cache.get(self._cache_key)
        return list(
            {
                pickle.loads(codecs.decode(plugin.encode(), "base64"))
                for plugin in cached
            }
        )

    def _clear_plugins(self: "PluginManager") -> None:
        """Remove all plugins."""
        self._cache.set(self._cache_key, json.dumps([]))

    @property
    def plugins(self: "PluginManager") -> List[PluginT]:
        """Get all plugins."""
        return self._get_plugins()

    def methods(self: "PluginManager", name: str) -> Generator[Callable, None, None]:
        """Get methods of all registered plugins matching `name`."""
        for plugin in self.plugins:
            if hasattr(plugin, name):
                method = getattr(plugin, name)
                if callable(method):
                    yield method

    def reset(self: "PluginManager") -> None:
        """Remove all plugins."""
        self._index = 0
        self._cache = SyncCache(db=params.cache.database, **REDIS_CONFIG)
        return self._clear_plugins()

    def unregister(self: "PluginManager", plugin: PluginT) -> None:
        """Remove a plugin from currently active plugins."""
        if isclass(plugin):
            if issubclass(plugin, HyperglassPlugin):
                plugins = {
                    # Create a base64 representation of a picked plugin.
                    codecs.encode(pickle.dumps(p), "base64").decode()
                    # Merge current plugins with the new plugin.
                    for p in self._get_plugins()
                    if p != plugin
                }
                # Add plugins from cache.
                self._cache.set(
                    f"hyperglass.plugins.{self._type}", json.dumps(list(plugins))
                )
                return
        raise PluginError("Plugin '{}' is not a valid hyperglass plugin", repr(plugin))

    def register(self: "PluginManager", plugin: PluginT) -> None:
        """Add a plugin to currently active plugins."""
        # Create a set of plugins so duplicate plugins are not mistakenly added.
        try:
            if issubclass(plugin, HyperglassPlugin):
                instance = plugin()
                plugins = {
                    # Create a base64 representation of a picked plugin.
                    codecs.encode(pickle.dumps(p), "base64").decode()
                    # Merge current plugins with the new plugin.
                    for p in [*self._get_plugins(), instance]
                }
                # Add plugins from cache.
                self._cache.set(
                    f"hyperglass.plugins.{self._type}", json.dumps(list(plugins))
                )
                log.success("Registered plugin '{}'", instance.name)
                return
        except TypeError:
            raise PluginError(
                "Plugin '{p}' has not defined a required method. "
                "Please consult the hyperglass documentation.",
                p=repr(plugin),
            )
        raise PluginError(
            "Plugin '{p}' is not a valid hyperglass plugin", p=repr(plugin)
        )


class InputPluginManager(PluginManager[InputPlugin], type="input"):
    """Manage Input Validation Plugins."""


class OutputPluginManager(PluginManager[OutputPlugin], type="output"):
    """Manage Output Processing Plugins."""
