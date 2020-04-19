"""Session handler for Slack API."""

# Project
from hyperglass.log import log
from hyperglass.models import Webhook
from hyperglass.external._base import BaseExternal


class SlackHook(BaseExternal, name="Slack"):
    """Slack session handler."""

    def __init__(self):
        """Initialize external base class with Slack connection details."""

        super().__init__(base_url="https://hooks.slack.com")

    async def send(self, query, provider):
        """Send an incoming webhook to Slack."""

        payload = Webhook(**query)

        log.debug("Sending query data to Slack:\n{}", payload)

        return await self._apost(endpoint=provider.host.path, data=payload.slack())
