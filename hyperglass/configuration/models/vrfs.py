"""
Defines models for VRF config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List
from typing import Dict
from ipaddress import IPv4Network
from ipaddress import IPv6Network

# Third Party Imports
from pydantic import constr
from pydantic import IPvAnyNetwork
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models._utils import HyperglassModel

from logzero import logger as log


class Vrf(HyperglassModel):
    """Model for per VRF/afi config in devices.yaml"""

    display_name: str
    ipv4: bool = True
    ipv6: bool = True
    access_list: List[Dict[constr(regex=("allow|deny")), IPvAnyNetwork]] = [
        {"allow": "0.0.0.0/0"},
        {"allow": "::/0"},
    ]

    @validator("access_list", pre=True, whole=True, always=True)
    def validate_action(cls, value):
        for li in value:
            for action, network in li.items():
                if isinstance(network, (IPv4Network, IPv6Network)):
                    li[action] = str(network)
        log.info(value)
        return value


class Vrfs(HyperglassModel):
    """Base model for vrfs class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from VRF names, dynamically sets attributes for
        the Vrfs class.
        """

        # Default settings which include the default/global routing table
        vrfs: Vrf = {"default": {"display_name": "Global", "ipv4": True, "ipv6": True}}
        display_names: List[str] = ["Global"]
        _all: List[str] = ["global"]

        for (vrf_key, params) in input_params.items():
            vrf = clean_name(vrf_key)
            vrf_params = Vrf(**params)
            vrfs.update({vrf: vrf_params.dict()})
            display_names.append(params.get("display_name"))
            _all.append(vrf_key)
        for (vrf_key, params) in vrfs.items():
            setattr(Vrfs, vrf_key, Vrf(**params))

        display_names: List[str] = list(set(display_names))
        _all: List[str] = list(set(_all))
        Vrfs.vrfs = vrfs
        Vrfs.display_names = display_names
        Vrfs._all = _all
        return Vrfs()
