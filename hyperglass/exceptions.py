"""Custom exceptions for hyperglass."""

import json as _json
from hyperglass.util import log


class HyperglassError(Exception):
    """hyperglass base exception."""

    def __init__(self, message="", alert="warning", keywords=None):
        """Initialize the hyperglass base exception class.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            alert {str} -- Error severity (default: {"warning"})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self.message = message
        self.alert = alert
        self.keywords = keywords or []
        if self.alert == "warning":
            log.error(repr(self))
        elif self.alert == "danger":
            log.critical(repr(self))
        else:
            log.info(repr(self))

    def __str__(self):
        """Return the instance's error message.

        Returns:
            {str} -- Error Message
        """
        return self.message

    def __repr__(self):
        """Return the instance's severity & error message in a string.

        Returns:
            {str} -- Error message with code
        """
        return f"[{self.alert.upper()}] {self.message}"

    def __dict__(self):
        """Return the instance's attributes as a dictionary.

        Returns:
            {dict} -- Exception attributes in dict
        """
        return {"message": self.message, "alert": self.alert, "keywords": self.keywords}

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
        return self.message

    @property
    def alert(self):
        """Return the instance's `alert` attribute.

        Returns:
            {str} -- Alert name
        """
        return self.alert

    @property
    def keywords(self):
        """Return the instance's `keywords` attribute.

        Returns:
            {list} -- Keywords List
        """
        return self.keywords


class _UnformattedHyperglassError(HyperglassError):
    """Base exception class for freeform error messages."""

    def __init__(self, unformatted_msg, alert="warning", **kwargs):
        """Format error message with keyword arguments.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            alert {str} -- Error severity (default: {"warning"})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self.message = unformatted_msg.format(**kwargs)
        self.alert = alert
        self.keywords = list(kwargs.values())
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class ConfigError(_UnformattedHyperglassError):
    """Raised for generic user-config issues."""


class ConfigInvalid(_UnformattedHyperglassError):
    """Raised when a config item fails type or option validation."""

    message = 'The value field "{field}" is invalid: {error_msg}'


class ConfigMissing(_UnformattedHyperglassError):
    """Raised when a required config file or item is missing or undefined."""

    message = (
        "{missing_item} is missing or undefined and is required to start "
        "hyperglass. Please consult the installation documentation."
    )


class ScrapeError(_UnformattedHyperglassError):
    """Raised when a scrape/netmiko error occurs."""

    alert = "danger"


class AuthError(_UnformattedHyperglassError):
    """Raised when authentication to a device fails."""

    alert = "danger"


class RestError(_UnformattedHyperglassError):
    """Raised upon a rest API client error."""

    alert = "danger"


class DeviceTimeout(_UnformattedHyperglassError):
    """Raised when the connection to a device times out."""

    alert = "danger"


class InputInvalid(_UnformattedHyperglassError):
    """Raised when input validation fails."""


class InputNotAllowed(_UnformattedHyperglassError):
    """Raised when input validation fails due to a configured check."""


class ResponseEmpty(_UnformattedHyperglassError):
    """Raised when hyperglass can connect to the device but the response is empty."""


class UnsupportedDevice(_UnformattedHyperglassError):
    """Raised when an input NOS is not in the supported NOS list."""
