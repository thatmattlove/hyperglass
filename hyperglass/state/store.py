"""Primary state container."""

# Standard Library
import codecs
import pickle
import typing as t

# Project
from hyperglass.configuration import params, devices, ui_params, directives

# Local
from .manager import StateManager

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.ui import UIParameters
    from hyperglass.models.system import HyperglassSystem
    from hyperglass.plugins._base import HyperglassPlugin
    from hyperglass.models.directive import Directive, Directives
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices


PluginT = t.TypeVar("PluginT", bound="HyperglassPlugin")


class HyperglassState(StateManager):
    """Primary hyperglass state container."""

    def __init__(self, *, settings: "HyperglassSystem") -> None:
        """Initialize state store and reset plugins."""
        super().__init__(settings=settings)

        # Add configuration objects.
        self.redis.set("params", params)
        self.redis.set("devices", devices)
        self.redis.set("ui_params", ui_params)
        self.redis.set("directives", directives)

        # Ensure plugins are empty.
        self.reset_plugins("output")
        self.reset_plugins("input")

    def add_plugin(self, _type: str, plugin: "HyperglassPlugin") -> None:
        """Add a plugin to its list by type."""
        current = self.plugins(_type)
        plugins = {
            # Create a base64 representation of a picked plugin.
            codecs.encode(pickle.dumps(p), "base64").decode()
            # Merge current plugins with the new plugin.
            for p in [*current, plugin]
        }
        self.redis.set(("plugins", _type), list(plugins))

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
        current = self.redis.get(("plugins", _type), raise_if_none=False, value_if_none=[])
        return list({pickle.loads(codecs.decode(plugin.encode(), "base64")) for plugin in current})
