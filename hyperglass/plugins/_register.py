"""Plugin registration."""

# Standard Library
import json
import codecs
import pickle
from typing import List, Generator

# Project
from hyperglass.log import log
from hyperglass.cache import SyncCache
from hyperglass.configuration import REDIS_CONFIG, params

# Local
from ._output import OutputPlugin

CACHE = SyncCache(db=params.cache.database, **REDIS_CONFIG)


def get_plugins() -> Generator[OutputPlugin, None, None]:
    """Retrieve plugins from cache."""
    # Retrieve plugins from cache.
    raw = CACHE.get("hyperglass.plugins.output")
    if isinstance(raw, List):
        for plugin in raw:
            yield pickle.loads(codecs.decode(plugin.encode(), "base64"))


def add_plugin(plugin: OutputPlugin) -> None:
    """Add a plugin to currently active plugins."""
    # Create a set of plugins so duplicate plugins are not mistakenly added.
    plugins = {
        # Create a base64 representation of a picked plugin.
        codecs.encode(pickle.dumps(p), "base64").decode()
        # Merge current plugins with the new plugin.
        for p in [*get_plugins(), plugin]
    }
    # Add plugins from cache.
    CACHE.set("hyperglass.plugins.output", json.dumps(list(plugins)))


def register_output_plugin(plugin: OutputPlugin):
    """Register an output plugin."""
    if issubclass(plugin, OutputPlugin):
        plugin = plugin()
        add_plugin(plugin)
        log.info("Registered output plugin '{}'", plugin.__class__.__name__)
