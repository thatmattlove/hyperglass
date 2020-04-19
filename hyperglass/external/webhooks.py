"""Convenience functions for webhooks."""

# Project
from hyperglass.exceptions import HyperglassError
from hyperglass.external._base import BaseExternal
from hyperglass.external.slack import SlackHook

PROVIDER_MAP = {
    "slack": SlackHook,
}


class Webhook(BaseExternal):
    """Get webhook for provider name."""

    def __new__(cls, provider):
        """Return instance for correct provider handler."""
        try:
            provider_class = PROVIDER_MAP[provider]
            return provider_class()
        except KeyError:
            raise HyperglassError(
                f"{provider} is not yet supported as a webhook target."
            )
