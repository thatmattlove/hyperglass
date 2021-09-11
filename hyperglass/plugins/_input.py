"""Input validation plugins."""

# Standard Library
from abc import abstractmethod

# Project
from hyperglass.models.api.query import Query

# Local
from ._base import HyperglassPlugin


class InputPlugin(HyperglassPlugin):
    """Plugin to validate user input prior to running commands."""

    @abstractmethod
    def process(self, device_output: str, query: Query) -> str:
        """Validate input from hyperglass UI/API."""
        pass
