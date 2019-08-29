"""
Custom exceptions for hyperglass
"""

import string
from typing import Union, List

from hyperglass.constants import code


class HyperglassError(Exception):
    """
    hyperglass base exception
    """

    message: str = ""
    formatter: string.Formatter = string.Formatter()

    def __init__(self, **kwargs: Union[str, int]) -> None:
        """
        Exception arguments are accepted as kwargs, but a check is
        performed to ensure that all format string parameters are passed
        in, and no extras are given.
        """
        self._kwargs = kwargs
        self._error_check()
        super().__init__(str(self))

    def _error_check(self) -> None:
        required = set(
            arg for _, arg, _, _ in self.formatter.parse(self.message) if arg
        )
        given = set(self._kwargs.keys())

        missing = required.difference(given)
        if missing:
            raise TypeError(
                "{name} missing requred arguments: {missing}".format(
                    name=self.__class__.__name__, missing=missing
                )
            )

        extra = given.difference(required)
        if extra:
            raise TypeError(
                "{name} given extra arguments: {extra}".format(
                    name=self.__class__.__name__, extra=extra
                )
            )

    def __str__(self) -> str:
        return self.formatter.format(self.message, **self._kwargs)

    def __getattr__(self, key: str) -> str:
        """
        Any exception kwargs arguments are accessible by name on the
        object.
        """
        remind = ""
        if "_kwargs" not in self.__dict__:
            remind = "(Did you forget to call super().__init__(**kwargs)?)"

        elif key in self._kwargs:
            return self._kwargs[key]

        raise AttributeError(
            "{name!r} object has no attribute {key!r} {remind}".format(
                name=self.__class__.__name__, key=key, remind=remind
            ).strip()
        )


class ConfigError(HyperglassError):
    """
    Raised for generic user-config issues.
    """

    message: str = "{error_msg}"


class ConfigInvalid(HyperglassError):
    """Raised when a config item fails type or option validation"""

    message: str = 'The value field "{field}" is invalid: {error_msg}'


class ConfigMissing(HyperglassError):
    """
    Raised when a required config file or item is missing or undefined
    """

    message: str = (
        "{missing_item} is missing or undefined and is required to start "
        "hyperglass. Please consult the installation documentation."
    )


class ScrapeError(HyperglassError):
    """Raised upon a scrape/netmiko error"""

    message: str = ""
    status: int = code.target_error


class AuthError(HyperglassError):
    """Raised when authentication to a device fails"""

    message: str = ""
    status: int = code.target_error


class RestError(HyperglassError):
    """Raised upon a rest API client error"""

    message: str = ""
    status: int = code.target_error


class InputInvalid(HyperglassError):
    """Raised when input validation fails"""

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._query_type = self._kwargs.get("query_type")
        if self._query_type in ("bgp_route", "ping", "traceroute"):
            self.query_type: str = "IP Address"
        elif self._query_type == "bgp_aspath":
            self.query_type: str = "AS Path"
        elif self._query_type == "bgp_community":
            self.query_type: str = "Community"
        self.target: str = str(kwargs.get("target"), None)
        self.message = f"{self.target} is an invalid {self.query_type}."
        self.status: int = code.invalid
        self.keywords: List[str] = []
        super().__init__(self.message, self.status, self.keywords)

    def __str__(self):
        return self.message


class InputNotAllowed(HyperglassError):
    """
    Raised when input validation fails due to a blacklist or
    requires_ipv6_cidr check
    """

    message: str = ""
    status: int = code.not_allowed
    keywords: List[str] = []


class ParseError(HyperglassError):
    """
    Raised when an ouput parser encounters an error.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class UnsupportedDevice(HyperglassError):
    """
    Raised when an input NOS is not in the supported NOS list.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
