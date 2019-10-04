"""
Defines models for Router config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List
from typing import Union

from ipaddress import IPv4Address, IPv6Address

# Third Party Imports
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.constants import Supported
from hyperglass.exceptions import UnsupportedDevice
from hyperglass.exceptions import ConfigError


class DeviceVrf4(HyperglassModel):
    """Model for AFI definitions"""

    afi_name: str = ""
    vrf_name: str = ""
    source_address: IPv4Address

    @validator("source_address")
    def stringify_ip(cls, v):
        if isinstance(v, IPv4Address):
            v = str(v)
        return v


class DeviceVrf6(HyperglassModel):
    """Model for AFI definitions"""

    afi_name: str = ""
    vrf_name: str = ""
    source_address: IPv6Address

    @validator("source_address")
    def stringify_ip(cls, v):
        if isinstance(v, IPv6Address):
            v = str(v)
        return v


class VrfAfis(HyperglassModel):
    """Model for per-AFI dicts of VRF params"""

    ipv4: Union[DeviceVrf4, None] = None
    ipv6: Union[DeviceVrf6, None] = None


class Vrf(HyperglassModel):
    default: VrfAfis

    class Config:
        """Pydantic Config Overrides"""

        extra = "allow"


class Router(HyperglassModel):
    """Model for per-router config in devices.yaml."""

    address: str
    network: str
    credential: str
    proxy: Union[str, None] = None
    location: str
    display_name: str
    port: int
    nos: str
    commands: Union[str, None] = None
    vrfs: Vrf
    _vrfs: List[str]
    display_vrfs: List[str] = []

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

    @validator("vrfs", pre=True, whole=True, always=True)
    def validate_vrfs(cls, v, values):  # noqa: N805
        """
        If an AFI map is not defined, try to get one based on the
        NOS name. If that doesn't exist, use a default.
        """
        _vrfs = []
        for vrf_label, vrf_afis in v.items():
            if vrf_label is None:
                raise ConfigError(
                    "The default routing table with source IPs must be defined"
                )
            vrf_label = clean_name(vrf_label)
            _vrfs.append(vrf_label)
            if not vrf_afis.get("ipv4"):
                vrf_afis.update({"ipv4": None})
            if not vrf_afis.get("ipv6"):
                vrf_afis.update({"ipv6": None})
            for afi, params in {
                a: p for a, p in vrf_afis.items() if p is not None
            }.items():
                if not params.get("source_address"):
                    raise ConfigError(
                        'A "source_address" must be defined in {afi}', afi=afi
                    )
                if not params.get("afi_name"):
                    params.update({"afi_name": afi})
                if not params.get("vrf_name"):
                    params.update({"vrf_name": vrf_label})
            setattr(Vrf, vrf_label, VrfAfis(**vrf_afis))
        values["_vrfs"] = _vrfs
        return v

    class Config:
        """Pydantic Config Overrides"""

        extra = "allow"


class Routers(HyperglassModel):
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
