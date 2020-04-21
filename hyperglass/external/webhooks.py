"""Convenience functions for webhooks."""

# Project
from hyperglass.exceptions import HyperglassError
from hyperglass.external._base import BaseExternal
from hyperglass.external.slack import SlackHook
from hyperglass.external.generic import GenericHook

PROVIDER_MAP = {
    "slack": SlackHook,
    "generic": GenericHook,
}


class Webhook(BaseExternal):
    """Get webhook for provider name."""

    def __new__(cls, config):
        """Return instance for correct provider handler."""
        try:
            provider_class = PROVIDER_MAP[config.provider]
            return provider_class(config)
        except KeyError:
            raise HyperglassError(
                f"'{config.provider.title()}' is not yet supported as a webhook target."
            )
