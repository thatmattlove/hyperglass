"""
Custom exceptions for hyperglass
"""

from typing import Dict

from hyperglass.constants import code


class HyperglassError(Exception):
    """
    hyperglass base exception
    """

    pass


class ConfigError(HyperglassError):
    """
    Raised for generic user-config issues.
    """

    def __init__(self, unformatted_msg, kwargs={}):
        self.message: unformatted_msg.format(**kwargs)
        self.keywords: Dict = kwargs
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class ConfigInvalid(HyperglassError):
    """Raised when a config item fails type or option validation"""

    def __init__(self, **kwargs):
        self.message: str = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self.keywords: Dict = kwargs
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class ConfigMissing(HyperglassError):
    """
    Raised when a required config file or item is missing or undefined
    """

    def __init__(self, kwargs={}):
        self.message: str = (
            "{missing_item} is missing or undefined and is required to start "
            "hyperglass. Please consult the installation documentation."
        ).format(**kwargs)
        self.keywords: Dict = kwargs
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class ScrapeError(HyperglassError):
    """Raised upon a scrape/netmiko error"""

    def __init__(self, kwargs={}):
        self.message: str = "".format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.target_error
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class AuthError(HyperglassError):
    """Raised when authentication to a device fails"""

    def __init__(self, kwargs={}):
        self.message: str = "".format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.target_error
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class RestError(HyperglassError):
    """Raised upon a rest API client error"""

    def __init__(self, kwargs={}):
        self.message: str = "".format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.target_error
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class InputInvalid(HyperglassError):
    """Raised when input validation fails"""

    def __init__(self, unformatted_msg, **kwargs):
        self.message: str = unformatted_msg.format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.invalid
        super().__init__(self.message, self.status)

    def __str__(self):
        return self.message


class InputNotAllowed(HyperglassError):
    """
    Raised when input validation fails due to a blacklist or
    requires_ipv6_cidr check
    """

    def __init__(self, unformatted_msg, **kwargs):
        self.message: str = unformatted_msg.format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.invalid
        super().__init__(self.status, self.message)

    def __str__(self):
        return self.message


class ParseError(HyperglassError):
    """
    Raised when an ouput parser encounters an error.
    """

    def __init__(self, kwargs={}):
        self.message: str = "".format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.target_error
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message


class UnsupportedDevice(HyperglassError):
    """
    Raised when an input NOS is not in the supported NOS list.
    """

    def __init__(self, kwargs={}):
        self.message: str = "".format(**kwargs)
        self.keywords: Dict = kwargs
        self.status: int = code.target_error
        super().__init__(self.message, self.keywords)

    def __str__(self):
        return self.message
