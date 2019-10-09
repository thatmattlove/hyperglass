"""
Custom exceptions for hyperglass
"""


class HyperglassError(Exception):
    """hyperglass base exception"""

    def __init__(self, message="", alert="warning", keywords=[]):
        self.message = message
        self.alert = alert
        self.keywords = keywords

    def __str__(self):
        return self.message

    def __dict__(self):
        return {"message": self.message, "alert": self.alert, "keywords": self.keywords}


class ConfigError(HyperglassError):
    """Raised for generic user-config issues."""

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)


class ConfigInvalid(HyperglassError):
    """Raised when a config item fails type or option validation"""

    def __init__(self, **kwargs):
        self.message = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)


class ConfigMissing(HyperglassError):
    """
    Raised when a required config file or item is missing or undefined.
    """

    def __init__(self, **kwargs):
        self.message = (
            "{missing_item} is missing or undefined and is required to start "
            "hyperglass. Please consult the installation documentation."
        ).format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)


class ScrapeError(HyperglassError):
    """Raised upon a scrape/netmiko error"""

    def __init__(self, msg, **kwargs):
        self.message = msg.format(**kwargs)
        self.alert = "danger"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class AuthError(HyperglassError):
    """Raised when authentication to a device fails"""

    def __init__(self, msg, **kwargs):
        self.message = msg.format(**kwargs)
        self.alert = "danger"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class RestError(HyperglassError):
    """Raised upon a rest API client error"""

    def __init__(self, msg, **kwargs):
        self.message = msg.format(**kwargs)
        self.alert = "danger"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class InputInvalid(HyperglassError):
    """Raised when input validation fails"""

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.alert = "warning"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class InputNotAllowed(HyperglassError):
    """
    Raised when input validation fails due to a blacklist or
    requires_ipv6_cidr check
    """

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.alert = "warning"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class ResponseEmpty(HyperglassError):
    """
    Raised when hyperglass is able to connect to the device and execute
    a valid query, but the response is empty.
    """

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.alert = "warning"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)


class UnsupportedDevice(HyperglassError):
    """Raised when an input NOS is not in the supported NOS list."""

    def __init__(self, **kwargs):
        self.message = "".format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)


class DeviceTimeout(HyperglassError):
    """Raised when the connection to a device times out."""

    def __init__(self, msg, **kwargs):
        self.message = msg.format(**kwargs)
        self.alert = "danger"
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, alert=self.alert, keywords=self.keywords)
