"""Custom Pydantic Fields/Types."""

# Standard Library
import re
import typing as t
from pathlib import Path

# Third Party
from pydantic import StrictInt, StrictFloat

IntFloat = t.TypeVar("IntFloat", StrictInt, StrictFloat)
J = t.TypeVar("J")

SupportedDriver = t.Literal["netmiko", "hyperglass_agent"]
HttpAuthMode = t.Literal["basic", "api_key"]
HttpProvider = t.Literal["msteams", "slack", "generic"]
LogFormat = t.Literal["text", "json"]
Primitives = t.Union[None, float, int, bool, str]
JsonValue = t.Union[J, t.Sequence[J], t.Dict[str, J]]


class AnyUri(str):
    """Custom field type for HTTP URI, e.g. /example."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
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


class Action(str):
    """Custom field type for policy actions."""

    permits = ("permit", "allow", "accept")
    denies = ("deny", "block", "reject")

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        """Ensure action is an allowed value or acceptable alias."""
        if not isinstance(value, str):
            raise TypeError("Action type must be a string")
        value = value.strip().lower()

        if value in cls.permits:
            return cls("permit")
        if value in cls.denies:
            return cls("deny")

        raise ValueError(
            "Action must be one of '{}'".format(", ".join((*cls.permits, *cls.denies)))
        )

    def __repr__(self):
        """Stringify custom field representation."""
        return f"Action({super().__repr__()})"


class HttpMethod(str):
    """Custom field type for HTTP methods."""

    methods = (
        "CONNECT",
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
        "TRACE",
    )

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        """Ensure http method is valid."""
        if not isinstance(value, str):
            raise TypeError("HTTP Method must be a string")
        value = value.strip().upper()

        if value in cls.methods:
            return cls(value)

        raise ValueError("HTTP Method must be one of {!r}".format(", ".join(cls.methods)))

    def __repr__(self):
        """Stringify custom field representation."""
        return f"HttpMethod({super().__repr__()})"


class ConfigPathItem(Path):
    """Custom field type for files or directories contained within app_path."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value: Path) -> Path:
        """Ensure path is within app path."""

        if isinstance(value, str):
            value = Path(value)

        if not isinstance(value, Path):
            raise TypeError("Unable to convert type {} to ConfigPathItem".format(type(value)))

        # Project
        from hyperglass.settings import Settings

        if not value.is_relative_to(Settings.app_path):
            raise ValueError("{!s} must be relative to {!s}".format(value, Settings.app_path))

        if Settings.container:
            value = Settings.default_app_path.joinpath(
                *(p for p in value.parts if p not in Settings.app_path.parts)
            )
        return value

    def __repr__(self):
        """Stringify custom field representation."""
        return f"ConfigPathItem({super().__repr__()})"
