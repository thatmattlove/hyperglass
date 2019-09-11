"""
Defines models for Router config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import Union

# Third Party Imports
from pydantic import BaseSettings
from pydantic import IPvAnyAddress
from pydantic import SecretStr
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import clean_name
from hyperglass.exceptions import UnsupportedDevice


class Proxy(BaseSettings):
    """Model for per-proxy config in devices.yaml"""

    address: Union[IPvAnyAddress, str]
    port: int = 22
    username: str
    password: SecretStr
    nos: str
    ssh_command: str

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """
        Validates that passed nos string is supported by hyperglass.
        """
        if not v == "linux_ssh":
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v


class Proxies(BaseSettings):
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

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True
