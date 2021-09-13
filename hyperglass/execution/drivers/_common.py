"""Base Connection Class."""

# Standard Library
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Sequence

# Project
from hyperglass.log import log
from hyperglass.plugins import OutputPluginManager

# Local
from ._construct import Construct

if TYPE_CHECKING:
    # Project
    from hyperglass.models.api import Query
    from hyperglass.models.data import OutputDataModel
    from hyperglass.compat._sshtunnel import SSHTunnelForwarder
    from hyperglass.models.config.devices import Device


class Connection(ABC):
    """Base transport driver class."""

    def __init__(self, device: "Device", query_data: "Query") -> None:
        """Initialize connection to device."""
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data.query_type
        self.query_target = self.query_data.query_target
        self._query = Construct(device=self.device, query=self.query_data)
        self.query = self._query.queries()
        self.plugin_manager = OutputPluginManager()

    @abstractmethod
    def setup_proxy(self: "Connection") -> "SSHTunnelForwarder":
        """Return a preconfigured sshtunnel.SSHTunnelForwarder instance."""
        pass

    async def response(self, output: Sequence[str]) -> Union[OutputDataModel, str]:
        """Send output through common parsers."""

        log.debug("Pre-parsed responses:\n{}", output)

        response = self.plugin_manager.execute(
            directive=self.query_data.directive, output=output, device=self.device
        )

        if response is None:
            response = "\n\n".join(output)

        log.debug("Post-parsed responses:\n{}", response)
        return response
