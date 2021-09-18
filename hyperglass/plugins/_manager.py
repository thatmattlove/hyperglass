"""Plugin manager definition."""

# Standard Library
import typing as t
from inspect import isclass

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.exceptions.private import PluginError

# Local
from ._base import PluginType, HyperglassPlugin
from ._input import InputPlugin, InputPluginReturn
from ._output import OutputType, OutputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.state import HyperglassState
    from hyperglass.models.api.query import Query
    from hyperglass.models.directive import Directive

PluginT = t.TypeVar("PluginT", bound=HyperglassPlugin)


class PluginManager(t.Generic[PluginT]):
    """Manage all plugins."""

    _type: PluginType
    _state: "HyperglassState"
    _index: int = 0
    _cache_key: str

    def __init__(self: "PluginManager") -> None:
        """Initialize plugin manager."""
        self._state = use_state()
        self._cache_key = f"hyperglass.plugins.{self._type}"

    def __init_subclass__(cls: "PluginManager", **kwargs: PluginType) -> None:
        """Set this plugin manager's type on subclass initialization."""
        _type = kwargs.get("type", None) or cls._type
        if _type is None:
            raise PluginError("Plugin '{}' is missing a 'type', keyword argument", repr(cls))
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

    @property
    def plugins(self: "PluginManager", builtins: bool = True) -> t.List[PluginT]:
        """Get all plugins, with built-in plugins last."""
        plugins = self._state.plugins(self._type)
        if builtins is False:
            plugins = [p for p in plugins if p.__hyperglass_builtin__ is False]

        # Sort plugins by their name attribute, which is the name of the class by default.
        sorted_by_name = sorted(plugins, key=lambda p: str(p))

        # Sort with built-in plugins last.
        return sorted(
            sorted_by_name,
            key=lambda p: -1 if p.__hyperglass_builtin__ else 1,  # flake8: noqa IF100
            reverse=True,
        )

    @property
    def name(self: PluginT) -> str:
        """Get this plugin manager's name."""
        return self.__class__.__name__

    def methods(self: "PluginManager", name: str) -> t.Generator[t.Callable, None, None]:
        """Get methods of all registered plugins matching `name`."""
        for plugin in self.plugins:
            if hasattr(plugin, name):
                method = getattr(plugin, name)
                if callable(method):
                    yield method

    def execute(self, *args, **kwargs) -> None:
        """Gather all plugins and execute in order."""
        raise NotImplementedError(f"Plugin Manager '{self.name}' is missing an 'execute()' method.")

    def reset(self: "PluginManager") -> None:
        """Remove all plugins."""
        self._index = 0
        self._state.reset_plugins(self._type)

    def unregister(self: "PluginManager", plugin: PluginT) -> None:
        """Remove a plugin from currently active plugins."""
        if isclass(plugin):
            if issubclass(plugin, HyperglassPlugin):
                self._state.remove_plugin(self._type, plugin)

                return
        raise PluginError("Plugin '{}' is not a valid hyperglass plugin", repr(plugin))

    def register(self: "PluginManager", plugin: PluginT, *args: t.Any, **kwargs: t.Any) -> None:
        """Add a plugin to currently active plugins."""
        # Create a set of plugins so duplicate plugins are not mistakenly added.
        try:
            if issubclass(plugin, HyperglassPlugin):
                instance = plugin(*args, **kwargs)
                self._state.add_plugin(self._type, instance)
                if instance.__hyperglass_builtin__ is True:
                    log.debug("Registered built-in plugin '{}'", instance.name)
                else:
                    log.success("Registered plugin '{}'", instance.name)
                return
        except TypeError:
            raise PluginError(
                "Plugin '{p}' has not defined a required method. "
                "Please consult the hyperglass documentation.",
                p=repr(plugin),
            )
        raise PluginError("Plugin '{p}' is not a valid hyperglass plugin", p=repr(plugin))


class InputPluginManager(PluginManager[InputPlugin], type="input"):
    """Manage Input Validation Plugins."""

    def execute(
        self: "InputPluginManager", *, directive: "Directive", query: "Query"
    ) -> InputPluginReturn:
        """Execute all input validation plugins.

        If any plugin returns `False`, execution is halted.
        """
        result = None
        for plugin in (plugin for plugin in self.plugins if directive.id in plugin.directives):
            if result is False:
                return result
            result = plugin.validate(query)
        return result


class OutputPluginManager(PluginManager[OutputPlugin], type="output"):
    """Manage Output Processing Plugins."""

    def execute(self: "OutputPluginManager", *, output: OutputType, query: "Query") -> OutputType:
        """Execute all output parsing plugins.

        The result of each plugin is passed to the next plugin.
        """
        result = output
        for plugin in (
            plugin for plugin in self.plugins if query.directive.id in plugin.directives
        ):
            if result is False:
                return result
            # Pass the result of each plugin to the next plugin.
            result = plugin.process(output=result, query=query)
        return result
