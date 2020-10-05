"""Session handler for Generic HTTP API endpoint."""

# Project
from hyperglass.log import log
from hyperglass.external._base import BaseExternal
from hyperglass.models.webhook import Webhook


class GenericHook(BaseExternal, name="Generic"):
    """Slack session handler."""

    def __init__(self, config):
        """Initialize external base class with http connection details."""

        super().__init__(
            base_url=f"{config.host.scheme}://{config.host.host}", config=config
        )

    async def send(self, query):
        """Send an incoming webhook to http endpoint."""

        payload = Webhook(**query)

        log.debug("Sending query data to {}:\n{}", self.config.host.host, payload)

        return await self._apost(
            endpoint=self.config.host.path,
            headers=self.config.headers,
            params=self.config.params,
            data=payload.export_dict(),
        )
