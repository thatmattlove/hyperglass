"""Input validation plugins."""

# Standard Library
from abc import abstractmethod
from typing import TYPE_CHECKING

# Local
from ._base import HyperglassPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query


class InputPlugin(HyperglassPlugin):
    """Plugin to validate user input prior to running commands."""

    @abstractmethod
    def process(self, device_output: str, query: "Query") -> str:
        """Validate input from hyperglass UI/API."""
        pass
