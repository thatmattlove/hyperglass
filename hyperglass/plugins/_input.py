"""Input validation plugins."""

# Standard Library
import typing as t

# Local
from ._base import DirectivePlugin, HyperglassPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query

InputPluginReturn = t.Union[None, bool]


class InputPlugin(HyperglassPlugin, DirectivePlugin):
    """Plugin to validate user input prior to running commands."""

    _type = "input"
    failure_reason: t.Optional[str] = None

    def validate(self, query: "Query") -> InputPluginReturn:
        """Validate input from hyperglass UI/API."""
        return None
