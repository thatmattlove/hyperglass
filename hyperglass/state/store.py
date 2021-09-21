"""Primary state container."""

# Standard Library
import typing as t

# Local
from .manager import StateManager

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.ui import UIParameters
    from hyperglass.plugins._base import HyperglassPlugin
    from hyperglass.models.directive import Directive, Directives
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices

    # Local
    from .manager import RedisManager


PluginT = t.TypeVar("PluginT", bound="HyperglassPlugin")


class HyperglassState(StateManager):
    """Primary hyperglass state container."""

    def add_plugin(self, _type: str, plugin: "HyperglassPlugin") -> None:
        """Add a plugin to its list by type."""
        current = self.plugins(_type)
        self.redis.set(("plugins", _type), list({*current, plugin}))

    def remove_plugin(self, _type: str, plugin: "HyperglassPlugin") -> None:
        """Remove a plugin from its list by type."""
        current = self.plugins(_type)
        plugins = {p for p in current if p != plugin}
        self.redis.set(("plugins", _type), list(plugins))

    def reset_plugins(self, _type: str) -> None:
        """Remove all plugins of `_type`."""
        self.redis.set(("plugins", _type), [])

    def add_directive(self, *directives: t.Union["Directive", t.Dict[str, t.Any]]) -> None:
        """Add a directive."""
        current = self.directives
        current.add(*directives, unique_by="id")
        self.redis.set("directives", current)

    def clear(self) -> None:
        """Delete all cache keys."""
        self.redis.instance.flushdb(asynchronous=True)

    @property
    def cache(self) -> "RedisManager":
        """Get the redis manager instance."""
        return self.redis

    @property
    def params(self) -> "Params":
        """Get hyperglass configuration parameters (`hyperglass.yaml`)."""
        return self.redis.get("params", raise_if_none=True)

    @property
    def devices(self) -> "Devices":
        """Get hyperglass devices (`devices.yaml`)."""
        return self.redis.get("devices", raise_if_none=True)

    @property
    def ui_params(self) -> "UIParameters":
        """UI parameters, built from params."""
        return self.redis.get("ui_params", raise_if_none=True)

    @property
    def directives(self) -> "Directives":
        """All directives."""
        return self.redis.get("directives", raise_if_none=True)

    def plugins(self, _type: str) -> t.List[PluginT]:
        """Get plugins by type."""
        return self.redis.get(("plugins", _type), raise_if_none=False, value_if_none=[])
