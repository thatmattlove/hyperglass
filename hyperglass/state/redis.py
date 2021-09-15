"""hyperglass global state."""

# Standard Library
import codecs
import pickle
import typing as t
from functools import lru_cache

# Third Party
from redis import Redis, ConnectionPool

# Project
from hyperglass.configuration import params, devices, ui_params
from hyperglass.exceptions.private import StateError

# Local
from ..settings import Settings

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.ui import UIParameters
    from hyperglass.models.system import HyperglassSystem
    from hyperglass.plugins._base import HyperglassPlugin
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices

PluginT = t.TypeVar("PluginT", bound="HyperglassPlugin")


class HyperglassState:
    """Global State Manager.

    Maintains configuration objects in Redis cache and accesses them as needed.
    """

    settings: "HyperglassSystem"
    redis: Redis
    _connection_pool: ConnectionPool
    _namespace: str = "hyperglass.state"

    def __init__(self, *, settings: "HyperglassSystem") -> None:
        """Set up Redis connection and add configuration objects."""

        self.settings = settings
        self._connection_pool = ConnectionPool.from_url(**self.settings.redis_connection_pool)
        self.redis = Redis(connection_pool=self._connection_pool)

        # Add configuration objects.
        self.set_object("params", params)
        self.set_object("devices", devices)
        self.set_object("ui_params", ui_params)

        # Ensure plugins are empty.
        self.reset_plugins("output")
        self.reset_plugins("input")

    def key(self, *keys: str) -> str:
        """Format keys with state namespace."""
        return ".".join((*self._namespace.split("."), *keys))

    def get_object(self, name: str, raise_if_none: bool = False) -> t.Any:
        """Get an object (class instance) from the cache."""
        value = self.redis.get(name)

        if isinstance(value, bytes):
            return pickle.loads(value)
        elif isinstance(value, str):
            return pickle.loads(value.encode())
        if raise_if_none is True:
            raise StateError("'{key}' does not exist in Redis store", key=name)
        return None

    def set_object(self, name: str, obj: t.Any) -> None:
        """Add an object (class instance) to the cache."""
        value = pickle.dumps(obj)
        self.redis.set(self.key(name), value)

    def add_plugin(self, _type: str, plugin: "HyperglassPlugin") -> None:
        """Add a plugin to its list by type."""
        current = self.plugins(_type)
        plugins = {
            # Create a base64 representation of a picked plugin.
            codecs.encode(pickle.dumps(p), "base64").decode()
            # Merge current plugins with the new plugin.
            for p in [*current, plugin]
        }
        self.set_object(self.key("plugins", _type), list(plugins))

    def remove_plugin(self, _type: str, plugin: "HyperglassPlugin") -> None:
        """Remove a plugin from its list by type."""
        current = self.plugins(_type)
        plugins = {
            # Create a base64 representation of a picked plugin.
            codecs.encode(pickle.dumps(p), "base64").decode()
            # Merge current plugins with the new plugin.
            for p in current
            if p != plugin
        }
        self.set_object(self.key("plugins", _type), list(plugins))

    def reset_plugins(self, _type: str) -> None:
        """Remove all plugins of `_type`."""
        self.set_object(self.key("plugins", _type), [])

    def clear(self) -> None:
        """Delete all cache keys."""
        self.redis.flushdb(asynchronous=True)

    @property
    def params(self) -> "Params":
        """Get hyperglass configuration parameters (`hyperglass.yaml`)."""
        return self.get_object(self.key("params"), raise_if_none=True)

    @property
    def devices(self) -> "Devices":
        """Get hyperglass devices (`devices.yaml`)."""
        return self.get_object(self.key("devices"), raise_if_none=True)

    @property
    def ui_params(self) -> "UIParameters":
        """UI parameters, built from params."""
        return self.get_object(self.key("ui_params"), raise_if_none=True)

    def plugins(self, _type: str) -> t.List[PluginT]:
        """Get plugins by type."""
        current = self.get_object(self.key("plugins", _type), raise_if_none=False) or []
        return list({pickle.loads(codecs.decode(plugin.encode(), "base64")) for plugin in current})


@lru_cache(maxsize=None)
def use_state() -> "HyperglassState":
    """Access hyperglass global state."""
    return HyperglassState(settings=Settings)
