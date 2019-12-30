"""Validate SSH proxy configuration variables."""

# Third Party Imports
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models.credentials import Credential
from hyperglass.exceptions import UnsupportedDevice


class Proxy(HyperglassModel):
    """Validation model for per-proxy config in devices.yaml."""

    name: str
    address: str
    port: int = 22
    credential: Credential
    nos: str = "linux_ssh"

    @validator("nos")
    def supported_nos(cls, value):  # noqa: N805
        """
        Validates that passed nos string is supported by hyperglass.
        """
        if not value == "linux_ssh":
            raise UnsupportedDevice(f'"{value}" device type is not supported.')
        return value


class Proxies(HyperglassModel):
    """Validation model for SSH proxy configuration."""

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
