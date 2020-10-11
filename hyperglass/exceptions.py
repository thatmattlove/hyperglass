"""Custom exceptions for hyperglass."""

# Standard Library
import json as _json
from typing import Dict, List, Union, Sequence

# Project
from hyperglass.log import log
from hyperglass.constants import STATUS_CODE_MAP


def validation_error_message(*errors: Dict) -> str:
    """Parse errors return from pydantic.ValidationError.errors()."""

    errs = ("\n",)

    for err in errors:
        loc = " → ".join(str(loc) for loc in err["loc"])
        errs += (f'Field: {loc}\n  Error: {err["msg"]}\n',)

    return "\n".join(errs)


class HyperglassError(Exception):
    """hyperglass base exception."""

    def __init__(self, message="", level="warning", keywords=None):
        """Initialize the hyperglass base exception class.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            level {str} -- Error severity (default: {"warning"})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self._message = message
        self._level = level
        self._keywords = keywords or []
        if self._level == "warning":
            log.error(repr(self))
        elif self._level == "danger":
            log.critical(repr(self))
        else:
            log.info(repr(self))

    def __str__(self):
        """Return the instance's error message.

        Returns:
            {str} -- Error Message
        """
        return self._message

    def __repr__(self):
        """Return the instance's severity & error message in a string.

        Returns:
            {str} -- Error message with code
        """
        return f"[{self.level.upper()}] {self._message}"

    def dict(self):
        """Return the instance's attributes as a dictionary.

        Returns:
            {dict} -- Exception attributes in dict
        """
        return {
            "message": self._message,
            "level": self._level,
            "keywords": self._keywords,
        }

    def json(self):
        """Return the instance's attributes as a JSON object.

        Returns:
            {str} -- Exception attributes as JSON
        """
        return _json.dumps(self.__dict__())

    @property
    def message(self):
        """Return the instance's `message` attribute.

        Returns:
            {str} -- Error Message
        """
        return self._message

    @property
    def level(self):
        """Return the instance's `level` attribute.

        Returns:
            {str} -- Alert name
        """
        return self._level

    @property
    def keywords(self):
        """Return the instance's `keywords` attribute.

        Returns:
            {list} -- Keywords List
        """
        return self._keywords

    @property
    def status_code(self):
        """Return HTTP status code based on level level.

        Returns:
            {int} -- HTTP Status Code
        """
        return STATUS_CODE_MAP.get(self._level, 500)


class _UnformattedHyperglassError(HyperglassError):
    """Base exception class for freeform error messages."""

    _level = "warning"

    def __init__(self, unformatted_msg="", level=None, **kwargs):
        """Format error message with keyword arguments.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            level {str} -- Error severity (default: {"warning"})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self._message = unformatted_msg.format(**kwargs)
        self._level = level or self._level
        self._keywords = list(kwargs.values())
        super().__init__(
            message=self._message, level=self._level, keywords=self._keywords
        )


class _PredefinedHyperglassError(HyperglassError):
    _message = "undefined"
    _level = "warning"

    def __init__(self, level=None, **kwargs):
        self._fmt_msg = self._message.format(**kwargs)
        self._level = level or self._level
        self._keywords = list(kwargs.values())
        super().__init__(
            message=self._fmt_msg, level=self._level, keywords=self._keywords
        )


class ConfigInvalid(HyperglassError):
    """Raised when a config item fails type or option validation."""

    def __init__(self, errors: List) -> None:
        """Parse Pydantic ValidationError."""

        super().__init__(message=validation_error_message(*errors))


class ConfigError(_UnformattedHyperglassError):
    """Raised for generic user-config issues."""


class ConfigMissing(_PredefinedHyperglassError):
    """Raised when a required config file or item is missing or undefined."""

    _message = (
        "{missing_item} is missing or undefined and is required to start "
        "hyperglass. Please consult the installation documentation."
    )


class ScrapeError(_UnformattedHyperglassError):
    """Raised when a scrape/netmiko error occurs."""

    _level = "danger"


class AuthError(_UnformattedHyperglassError):
    """Raised when authentication to a device fails."""

    _level = "danger"


class RestError(_UnformattedHyperglassError):
    """Raised upon a rest API client error."""

    _level = "danger"


class DeviceTimeout(_UnformattedHyperglassError):
    """Raised when the connection to a device times out."""

    _level = "danger"


class InputInvalid(_UnformattedHyperglassError):
    """Raised when input validation fails."""


class InputNotAllowed(_UnformattedHyperglassError):
    """Raised when input validation fails due to a configured check."""


class ResponseEmpty(_UnformattedHyperglassError):
    """Raised when hyperglass can connect to the device but the response is empty."""


class UnsupportedDevice(_UnformattedHyperglassError):
    """Raised when an input NOS is not in the supported NOS list."""


class ParsingError(_UnformattedHyperglassError):
    """Raised when there is a problem parsing a structured response."""

    def __init__(
        self,
        unformatted_msg: Union[Sequence[Dict], str],
        level: str = "danger",
        **kwargs,
    ):
        """Format error message with keyword arguments."""
        if isinstance(unformatted_msg, Sequence):
            self._message = validation_error_message(*unformatted_msg)
        else:
            self._message = unformatted_msg.format(**kwargs)
        self._level = level or self._level
        self._keywords = list(kwargs.values())
        super().__init__(
            message=self._message, level=self._level, keywords=self._keywords
        )
