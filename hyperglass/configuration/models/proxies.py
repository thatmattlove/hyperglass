"""
Defines models for Router config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Third Party Imports
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models.credentials import Credential
from hyperglass.exceptions import UnsupportedDevice


class Proxy(HyperglassModel):
    """Model for per-proxy config in devices.yaml"""

    name: str
    address: str
    port: int = 22
    credential: Credential
    nos: str = "linux_ssh"

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """
        Validates that passed nos string is supported by hyperglass.
        """
        if not v == "linux_ssh":
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v


class Proxies(HyperglassModel):
    """Base model for proxies class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the proxies class.
        """
        obj = Proxies()
        for (devname, params) in input_params.items():
            dev = clean_name(devname)
            setattr(Proxies, dev, Proxy(**params))
        return obj
