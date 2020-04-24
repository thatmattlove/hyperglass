"""Data models used throughout hyperglass."""

# Standard Library
import re
from typing import TypeVar, Optional

# Third Party
from pydantic import HttpUrl, BaseModel, StrictInt, StrictStr, StrictFloat

# Project
from hyperglass.log import log
from hyperglass.util import clean_name

IntFloat = TypeVar("IntFloat", StrictInt, StrictFloat)


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    class Config:
        """Default Pydantic configuration.

        See https://pydantic-docs.helpmanual.io/usage/model_config
        """

        validate_all = True
        extra = "forbid"
        validate_assignment = True
        alias_generator = clean_name
        json_encoders = {HttpUrl: lambda v: str(v)}

    def export_json(self, *args, **kwargs):
        """Return instance as JSON.

        Returns:
            {str} -- Stringified JSON.
        """

        export_kwargs = {
            "by_alias": True,
            "exclude_unset": False,
            **kwargs,
        }

        return self.json(*args, **export_kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary.

        Returns:
            {dict} -- Python dictionary.
        """
        export_kwargs = {
            "by_alias": True,
            "exclude_unset": False,
            **kwargs,
        }

        return self.dict(*args, **export_kwargs)

    def export_yaml(self, *args, **kwargs):
        """Return instance as YAML.

        Returns:
            {str} -- Stringified YAML.
        """
        import json
        import yaml

        export_kwargs = {
            "by_alias": kwargs.pop("by_alias", True),
            "exclude_unset": kwargs.pop("by_alias", False),
        }

        return yaml.safe_dump(
            json.loads(self.export_json(**export_kwargs)), *args, **kwargs
        )


class HyperglassModelExtra(HyperglassModel):
    """Model for hyperglass configuration models with dynamic fields."""

    pass

    class Config:
        """Default pydantic configuration."""

        extra = "allow"


class AnyUri(str):
    """Custom field type for HTTP URI, e.g. /example."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custim field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Ensure URI string contains a leading forward-slash."""
        uri_regex = re.compile(r"^(\/.*)$")
        if not isinstance(value, str):
            raise TypeError("AnyUri type must be a string")
        match = uri_regex.fullmatch(value)
        if not match:
            raise ValueError(
                "Invalid format. A URI must begin with a forward slash, e.g. '/example'"
            )
        return cls(match.group())

    def __repr__(self):
        """Stringify custom field representation."""
        return f"AnyUri({super().__repr__()})"


class StrictBytes(bytes):
    """Custom data type for a strict byte string.

    Used for validating the encoded JWT request payload.
    """

    @classmethod
    def __get_validators__(cls):
        """Yield Pydantic validator function.

        See: https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types

        Yields:
            {function} -- Validator
        """
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validate type.

        Arguments:
            value {Any} -- Pre-validated input

        Raises:
            TypeError: Raised if value is not bytes

        Returns:
            {object} -- Instantiated class
        """
        if not isinstance(value, bytes):
            raise TypeError("bytes required")
        return cls()

    def __repr__(self):
        """Return representation of object.

        Returns:
            {str} -- Representation
        """
        return f"StrictBytes({super().__repr__()})"


class WebhookHeaders(HyperglassModel):
    """Webhook data model."""

    content_length: Optional[StrictStr]
    accept: Optional[StrictStr]
    user_agent: Optional[StrictStr]
    content_type: Optional[StrictStr]
    referer: Optional[StrictStr]
    accept_encoding: Optional[StrictStr]
    accept_language: Optional[StrictStr]
    x_real_ip: Optional[StrictStr]
    x_forwarded_for: Optional[StrictStr]

    class Config:
        """Pydantic model config."""

        fields = {
            "content_length": "content-length",
            "user_agent": "user-agent",
            "content_type": "content-type",
            "accept_encoding": "accept-encoding",
            "accept_language": "accept-language",
            "x_real_ip": "x-real-ip",
            "x_forwarded_for": "x-forwarded-for",
        }


class WebhookNetwork(HyperglassModel):
    """Webhook data model."""

    prefix: Optional[StrictStr]
    asn: Optional[StrictStr]


class Webhook(HyperglassModel):
    """Webhook data model."""

    query_location: StrictStr
    query_type: StrictStr
    query_vrf: StrictStr
    query_target: StrictStr
    headers: WebhookHeaders
    source: StrictStr
    network: WebhookNetwork

    def slack(self):
        """Format the webhook data as a Slack message."""

        def make_field(key, value, code=False):
            if code:
                value = f"`{value}`"
            return f"*{key}*\n{value}"

        try:
            header_data = []
            for k, v in self.headers.dict(by_alias=True).items():
                field = make_field(k, v, code=True)
                header_data.append(field)

            query_details = (
                ("Query Location", self.query_location),
                ("Query Type", self.query_type),
                ("Query VRF", self.query_vrf),
                ("Query Target", self.query_target),
            )
            query_data = []
            for k, v in query_details:
                field = make_field(k, v)
                query_data.append({"type": "mrkdwn", "text": field})

            source_details = (
                ("Source IP", self.source),
                ("Source Prefix", self.network.prefix),
                ("Source ASN", self.network.asn),
            )

            source_data = []
            for k, v in source_details:
                field = make_field(k, v, code=True)
                source_data.append({"type": "mrkdwn", "text": field})

            payload = {
                "text": "hyperglass received a valid query with the following data",
                "blocks": [
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
        except Exception as err:
            log.error("Error while creating webhook: {}", str(err))
            payload = {}
        return payload
