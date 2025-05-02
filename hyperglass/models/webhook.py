"""Data models used throughout hyperglass."""

# Standard Library
import typing as t
from datetime import datetime

# Third Party
from pydantic import ConfigDict, model_validator

# Project
from hyperglass.log import log

# Local
from .main import HyperglassModel

_WEBHOOK_TITLE = "hyperglass received a valid query with the following data"
_ICON_URL = "https://res.cloudinary.com/hyperglass/image/upload/v1593192484/icon.png"


def to_snake_case(value: str) -> str:
    """Convert string to snake case."""
    return value.replace("_", "-")


class WebhookHeaders(HyperglassModel):
    """Webhook data model."""

    model_config = ConfigDict(alias_generator=to_snake_case)

    user_agent: t.Optional[str] = None
    referer: t.Optional[str] = None
    accept_encoding: t.Optional[str] = None
    accept_language: t.Optional[str] = None
    x_real_ip: t.Optional[str] = None
    x_forwarded_for: t.Optional[str] = None


class WebhookNetwork(HyperglassModel):
    """Webhook data model."""

    model_config = ConfigDict(extra="allow")

    prefix: str = "Unknown"
    asn: str = "Unknown"
    org: str = "Unknown"
    country: str = "Unknown"


class Webhook(HyperglassModel):
    """Webhook data model."""

    query_location: str
    query_type: str
    query_target: t.Union[t.List[str], str]
    headers: WebhookHeaders
    source: str = "Unknown"
    network: WebhookNetwork
    timestamp: datetime

    @model_validator(mode="before")
    def validate_webhook(cls, model: "Webhook") -> "Webhook":
        """Reset network attributes if the source is localhost."""
        if model.source in ("127.0.0.1", "::1"):
            model.network = {}
        return model

    def msteams(self) -> t.Dict[str, t.Any]:
        """Format the webhook data as a Microsoft Teams card."""

        def code(value: t.Any) -> str:
            """Wrap argument in backticks for markdown inline code formatting."""
            return f"`{str(value)}`"

        header_data = [
            {"name": k, "value": code(v)} for k, v in self.headers.model_dump(by_alias=True).items()
        ]
        time_fmt = self.timestamp.strftime("%Y %m %d %H:%M:%S")
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "118ab2",
            "summary": _WEBHOOK_TITLE,
            "sections": [
                {
                    "activityTitle": _WEBHOOK_TITLE,
                    "activitySubtitle": f"{time_fmt} UTC",
                    "activityImage": _ICON_URL,
                    "facts": [
                        {"name": "Query Location", "value": self.query_location},
                        {"name": "Query Target", "value": code(self.query_target)},
                        {"name": "Query Type", "value": self.query_type},
                    ],
                },
                {"markdown": True, "text": "**Source Information**"},
                {"markdown": True, "text": "---"},
                {
                    "markdown": True,
                    "facts": [
                        {"name": "IP", "value": code(self.source)},
                        {"name": "Prefix", "value": code(self.network.prefix)},
                        {"name": "ASN", "value": code(self.network.asn)},
                        {"name": "Country", "value": self.network.country},
                        {"name": "Organization", "value": self.network.org},
                    ],
                },
                {"markdown": True, "text": "**Request Headers**"},
                {"markdown": True, "text": "---"},
                {"markdown": True, "facts": header_data},
            ],
        }
        log.bind(type="MS Teams", payload=str(payload)).debug("Created webhook")

        return payload

    def slack(self) -> t.Dict[str, t.Any]:
        """Format the webhook data as a Slack message."""

        def make_field(key, value, code=False):
            if code:
                value = f"`{value}`"
            return f"*{key}*\n{value}"

        header_data = []
        for k, v in self.headers.model_dump(by_alias=True).items():
            field = make_field(k, v, code=True)
            header_data.append(field)

        query_data = [
            {"type": "mrkdwn", "text": make_field("Query Location", self.query_location)},
            {"type": "mrkdwn", "text": make_field("Query Target", self.query_target, code=True)},
            {"type": "mrkdwn", "text": make_field("Query Type", self.query_type)},
        ]

        source_data = [
            {"type": "mrkdwn", "text": make_field("Source IP", self.source, code=True)},
            {
                "type": "mrkdwn",
                "text": make_field("Source Prefix", self.network.prefix, code=True),
            },
            {"type": "mrkdwn", "text": make_field("Source ASN", self.network.asn, code=True)},
            {"type": "mrkdwn", "text": make_field("Source Country", self.network.country)},
            {"type": "mrkdwn", "text": make_field("Source Organization", self.network.org)},
        ]

        time_fmt = self.timestamp.strftime("%Y %m %d %H:%M:%S")

        payload = {
            "text": _WEBHOOK_TITLE,
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*{time_fmt} UTC*"}},
                {"type": "section", "fields": query_data},
                {"type": "divider"},
                {"type": "section", "fields": source_data},
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Headers*\n" + "\n".join(header_data)},
                },
            ],
        }
        log.bind(type="Slack", payload=str(payload)).debug("Created webhook")
        return payload
