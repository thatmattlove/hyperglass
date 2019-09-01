"""
Custom exceptions for hyperglass
"""

from hyperglass.constants import code


class HyperglassError(Exception):
    """
    hyperglass base exception
    """

    def __init__(self, message="", status=500, keywords={}):
        self.message = message
        self.status = status
        self.keywords = keywords

    def __dict__(self):
        return {
            "message": self.message,
            "status": self.status,
            "keywords": self.keywords,
        }


class ConfigError(HyperglassError):
    """
    Raised for generic user-config issues.
    """

    def __init__(self, unformatted_msg, kwargs={}):
        self.message = unformatted_msg.format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)

    def __str__(self):
        return self.message


class ConfigInvalid(HyperglassError):
    """Raised when a config item fails type or option validation"""

    def __init__(self, **kwargs):
        self.message = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)

    def __str__(self):
        return self.message


class ConfigMissing(HyperglassError):
    """
    Raised when a required config file or item is missing or undefined
    """

    def __init__(self, kwargs={}):
        self.message = (
            "{missing_item} is missing or undefined and is required to start "
            "hyperglass. Please consult the installation documentation."
        ).format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)

    def __str__(self):
        return self.message


class ScrapeError(HyperglassError):
    """Raised upon a scrape/netmiko error"""

    def __init__(self, msg, kwargs={}):
        self.message = msg.format(**kwargs)
        self.status = code.target_error
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message


class AuthError(HyperglassError):
    """Raised when authentication to a device fails"""

    def __init__(self, msg, kwargs={}):
        self.message = msg.format(**kwargs)
        self.status = code.target_error
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message


class RestError(HyperglassError):
    """Raised upon a rest API client error"""

    def __init__(self, msg, kwargs={}):
        self.message = msg.format(**kwargs)
        self.status = code.target_error
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message


class InputInvalid(HyperglassError):
    """Raised when input validation fails"""

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.status = code.invalid
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message


class InputNotAllowed(HyperglassError):
    """
    Raised when input validation fails due to a blacklist or
    requires_ipv6_cidr check
    """

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.status = code.invalid
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message


class UnsupportedDevice(HyperglassError):
    """
    Raised when an input NOS is not in the supported NOS list.
    """

    def __init__(self, kwargs={}):
        self.message = "".format(**kwargs)
        self.status = code.target_error
        self.keywords = [value for value in kwargs.values()]
        super().__init__(
            message=self.message, status=self.status, keywords=self.keywords
        )

    def __str__(self):
        return self.message
