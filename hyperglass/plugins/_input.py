"""Input validation plugins."""

# Standard Library
from typing import TYPE_CHECKING, Union

# Local
from ._base import DirectivePlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query

InputPluginReturn = Union[None, bool]


class InputPlugin(DirectivePlugin):
    """Plugin to validate user input prior to running commands."""

    def validate(self, query: "Query") -> InputPluginReturn:
        """Validate input from hyperglass UI/API."""
        return None
