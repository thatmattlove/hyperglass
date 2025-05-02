"""Convenience functions for webhooks."""

# Standard Library
import typing as t

# Project
from hyperglass.exceptions.private import UnsupportedError

# Local
from ._base import BaseExternal
from .slack import SlackHook
from .generic import GenericHook
from .msteams import MSTeams

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.config.logging import Http

PROVIDER_MAP = {
    "generic": GenericHook,
    "msteams": MSTeams,
    "slack": SlackHook,
}


class Webhook(BaseExternal):
    """Get webhook for provider name."""

    def __new__(cls: "Webhook", config: "Http") -> "BaseExternal":
        """Return instance for correct provider handler."""
        try:
            provider_class = PROVIDER_MAP[config.provider]
            return provider_class(config)
        except KeyError as err:
            raise UnsupportedError(
                message="{p} is not yet supported as a webhook target.",
                p=config.provider.title(),
            ) from err
