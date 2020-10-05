"""Data models used throughout hyperglass."""

# Standard Library
from typing import Optional
from datetime import datetime

# Third Party
from pydantic import StrictStr, root_validator

# Project
from hyperglass.log import log

from .main import HyperglassModel, HyperglassModelExtra

_WEBHOOK_TITLE = "hyperglass received a valid query with the following data"
_ICON_URL = "https://res.cloudinary.com/hyperglass/image/upload/v1593192484/icon.png"


class WebhookHeaders(HyperglassModel):
    """Webhook data model."""

    user_agent: Optional[StrictStr]
    referer: Optional[StrictStr]
    accept_encoding: Optional[StrictStr]
    accept_language: Optional[StrictStr]
    x_real_ip: Optional[StrictStr]
    x_forwarded_for: Optional[StrictStr]

    class Config:
        """Pydantic model config."""

        fields = {
            "user_agent": "user-agent",
            "accept_encoding": "accept-encoding",
            "accept_language": "accept-language",
            "x_real_ip": "x-real-ip",
            "x_forwarded_for": "x-forwarded-for",
        }


class WebhookNetwork(HyperglassModelExtra):
    """Webhook data model."""

    prefix: StrictStr = "Unknown"
    asn: StrictStr = "Unknown"
    org: StrictStr = "Unknown"
    country: StrictStr = "Unknown"


class Webhook(HyperglassModel):
    """Webhook data model."""

    query_location: StrictStr
    query_type: StrictStr
    query_vrf: StrictStr
    query_target: StrictStr
    headers: WebhookHeaders
    source: StrictStr = "Unknown"
    network: WebhookNetwork
    timestamp: datetime

    @root_validator(pre=True)
    def validate_webhook(cls, values):
        """Reset network attributes if the source is localhost."""
        if values.get("source") in ("127.0.0.1", "::1"):
            values["network"] = {}
        return values

    def msteams(self):
        """Format the webhook data as a Microsoft Teams card."""

        def code(value):
            """Wrap argument in backticks for markdown inline code formatting."""
            return f"`{str(value)}`"

        header_data = [
            {"name": k, "value": code(v)}
            for k, v in self.headers.dict(by_alias=True).items()
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
                        {"name": "Query VRF", "value": self.query_vrf},
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
        log.debug("Created MS Teams webhook: {}", str(payload))

        return payload

    def slack(self):
        """Format the webhook data as a Slack message."""

        def make_field(key, value, code=False):
            if code:
                value = f"`{value}`"
            return f"*{key}*\n{value}"

        header_data = []
        for k, v in self.headers.dict(by_alias=True).items():
            field = make_field(k, v, code=True)
            header_data.append(field)

        query_data = [
            {
                "type": "mrkdwn",
                "text": make_field("Query Location", self.query_location),
            },
            {
                "type": "mrkdwn",
                "text": make_field("Query Target", self.query_target, code=True),
            },
            {"type": "mrkdwn", "text": make_field("Query Type", self.query_type)},
            {"type": "mrkdwn", "text": make_field("Query VRF", self.query_vrf)},
        ]

        source_data = [
            {
                "type": "mrkdwn",
                "text": make_field("Source IP", self.source, code=True),
            },
            {
                "type": "mrkdwn",
                "text": make_field("Source Prefix", self.network.prefix, code=True),
            },
            {
                "type": "mrkdwn",
                "text": make_field("Source ASN", self.network.asn, code=True),
            },
            {
                "type": "mrkdwn",
                "text": make_field("Source Country", self.network.country),
            },
            {
                "type": "mrkdwn",
                "text": make_field("Source Organization", self.network.org),
            },
        ]

        time_fmt = self.timestamp.strftime("%Y %m %d %H:%M:%S")

        payload = {
            "text": _WEBHOOK_TITLE,
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{time_fmt} UTC*"},
                },
                {"type": "section", "fields": query_data},
                {"type": "divider"},
                {"type": "section", "fields": source_data},
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Headers*\n" + "\n".join(header_data),
                    },
                },
            ],
        }
        log.debug("Created Slack webhook: {}", str(payload))
        return payload
