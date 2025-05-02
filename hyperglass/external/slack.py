"""Session handler for Slack API."""

# Standard Library
import typing as t

# Project
from hyperglass.log import log
from hyperglass.external._base import BaseExternal
from hyperglass.models.webhook import Webhook

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.config.logging import Http


class SlackHook(BaseExternal, name="Slack"):
    """Slack session handler."""

    def __init__(self: "SlackHook", config: "Http") -> None:
        """Initialize external base class with Slack connection details."""

        super().__init__(base_url="https://hooks.slack.com", config=config, parse=False)

    async def send(self: "SlackHook", query: t.Dict[str, t.Any]):
        """Send an incoming webhook to Slack."""

        payload = Webhook(**query)
        log.bind(destination="Slack", payload=payload).debug("Sending request")

        return await self._apost(endpoint=self.config.host.path, data=payload.slack())
