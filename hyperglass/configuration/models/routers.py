"""
Defines models for Router config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List
from typing import Union

# Third Party Imports
from pydantic import BaseSettings
from pydantic import IPvAnyAddress
from pydantic import validator
from logzero import logger

# Project Imports
from hyperglass.configuration.models._utils import clean_name
from hyperglass.constants import Supported
from hyperglass.exceptions import UnsupportedDevice
from hyperglass.constants import afi_nos_map


class Afi(BaseSettings):
    """Model for AFI definitions"""

    label: str
    source: IPvAnyAddress


class Afis(BaseSettings):
    """Model for AFI map"""

    ipv4: Union[Afi, None] = None
    ipv6: Union[Afi, None] = None
    ipv4_vpn: Union[Afi, None] = None
    ipv6_vpn: Union[Afi, None] = None


class Router(BaseSettings):
    """Model for per-router config in devices.yaml."""

    address: Union[IPvAnyAddress, str]
    network: str
    credential: str
    proxy: Union[str, None] = None
    location: str
    display_name: str
    port: int
    nos: str
    commands: Union[str, None] = None
    vrfs: List[str] = ["default"]
    afis: Afis

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """
        Validates that passed nos string is supported by hyperglass.
        """
        if not Supported.is_supported(v):
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v

    @validator("credential", "proxy", "location")
    def clean_name(cls, v):  # noqa: N805
        """Remove or replace unsupported characters from field values"""
        return clean_name(v)

    @validator("commands", always=True)
    def validate_commands(cls, v, values):  # noqa: N805
        """
        If a named command profile is not defined, use theNOS name.
        """
        if v is None:
            v = values["nos"]
        return v

    @validator("afis", pre=True)
    def validate_afis(cls, v, values):  # noqa: N805
        """
        If an AFI map is not defined, try to get one based on the
        NOS name. If that doesn't exist, use a default.
        """
        logger.debug(f"V In: {v}")
        for (afi_name, afi_params) in {
            afi: params for afi, params in v.items() if params is not None
        }.items():
            if afi_params.get("label") is None:
                label = afi_nos_map.get(values["nos"], None)
                if label is None:
                    label = afi_nos_map["default"][afi_name]
                v[afi_name].update({"label": label})
        return v


class Routers(BaseSettings):
    """Base model for devices class."""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the Routers class.
        """
        routers = {}
        hostnames = []
        vrfs = set()
        for (devname, params) in input_params.items():
            dev = clean_name(devname)
            router_params = Router(**params)
            setattr(Routers, dev, router_params)
            routers.update({dev: router_params.dict()})
            hostnames.append(dev)
            for vrf in router_params.dict()["vrfs"]:
                vrfs.add(vrf)
        Routers.routers = routers
        Routers.hostnames = hostnames
        Routers.vrfs = list(vrfs)
        return Routers()

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True
