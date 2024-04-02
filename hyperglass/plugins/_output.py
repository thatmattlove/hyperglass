"""Device output plugins."""

# Standard Library
from typing import TYPE_CHECKING, Union

# Project
from hyperglass.log import log
from hyperglass.types import Series

# Local
from ._base import PlatformPlugin, DirectivePlugin, HyperglassPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query

OutputType = Union["OutputDataModel", Series[str]]


class OutputPlugin(HyperglassPlugin, DirectivePlugin, PlatformPlugin):
    """Plugin to interact with device command output."""

    _type = "output"

    def process(self, *, output: OutputType, query: "Query") -> OutputType:
        """Process or manipulate output from a device."""
        log.warning("Output plugin has not implemented a 'process()' method", plugin=self.name)
        return output
