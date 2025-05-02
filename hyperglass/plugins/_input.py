"""Input validation plugins."""

# Standard Library
import typing as t

# Local
from ._base import DirectivePlugin, HyperglassPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query


InputPluginValidationReturn = t.Union[None, bool]
InputPluginTransformReturn = t.Union[t.Sequence[str], str]


class InputPlugin(HyperglassPlugin, DirectivePlugin):
    """Plugin to validate user input prior to running commands."""

    _type = "input"
    failure_reason: t.Optional[str] = None

    def validate(self, query: "Query") -> InputPluginValidationReturn:
        """Validate input from hyperglass UI/API."""
        return None

    def transform(self, query: "Query") -> InputPluginTransformReturn:
        """Transform query target prior to running commands."""
        return query.query_target
