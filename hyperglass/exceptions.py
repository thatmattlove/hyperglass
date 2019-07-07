"""
Custom exceptions for hyperglass
"""


class HyperglassError(Exception):
    """
    hyperglass base exception.
    """

    pass


class ConfigError(HyperglassError):
    """
    Raised for user-inflicted configuration issues. Examples:
        - Fat fingered NOS in device definition
        - Used invalid type (str, int, etc.) in hyperglass.yaml
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class UnsupportedDevice(HyperglassError):
    """
    Raised when an input NOS is not in the supported NOS list.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
