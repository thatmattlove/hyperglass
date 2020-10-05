"""Session handler for Microsoft Teams API."""

# Project
from hyperglass.log import log
from hyperglass.external._base import BaseExternal
from hyperglass.models.webhook import Webhook


class MSTeams(BaseExternal, name="MSTeams"):
    """Microsoft Teams session handler."""

    def __init__(self, config):
        """Initialize external base class with Microsoft Teams connection details."""

        super().__init__(
            base_url="https://outlook.office.com", config=config, parse=False
        )

    async def send(self, query):
        """Send an incoming webhook to Microsoft Teams."""

        payload = Webhook(**query)

        log.debug("Sending query data to Microsoft Teams:\n{}", payload)

        return await self._apost(endpoint=self.config.host.path, data=payload.msteams())
