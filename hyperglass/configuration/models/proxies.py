"""Validate SSH proxy configuration variables."""

# Third Party
from pydantic import StrictInt, StrictStr, validator

# Project
from hyperglass.util import clean_name
from hyperglass.models import HyperglassModel
from hyperglass.exceptions import UnsupportedDevice
from hyperglass.configuration.models.credentials import Credential


class Proxy(HyperglassModel):
    """Validation model for per-proxy config in devices.yaml."""

    name: StrictStr
    address: StrictStr
    port: StrictInt = 22
    credential: Credential
    nos: StrictStr = "linux_ssh"

    @validator("nos")
    def supported_nos(cls, value):
        """Verify NOS is supported by hyperglass.

        Raises:
            UnsupportedDevice: Raised if NOS is not supported.

        Returns:
            {str} -- Valid NOS name
        """
        if not value == "linux_ssh":
            raise UnsupportedDevice(f'"{value}" device type is not supported.')
        return value


class Proxies(HyperglassModel):
    """Validation model for SSH proxy configuration."""

    @classmethod
    def import_params(cls, input_params):
        """Import loaded YAML, initialize per-proxy definitions.

        Remove unsupported characters from proxy names, dynamically
        set attributes for the proxies class.

        Arguments:
            input_params {dict} -- Unvalidated proxy definitions

        Returns:
            {object} -- Validated proxies object
        """
        obj = Proxies()
        for (devname, params) in input_params.items():
            dev = clean_name(devname)
            setattr(Proxies, dev, Proxy(**params))
        return obj
