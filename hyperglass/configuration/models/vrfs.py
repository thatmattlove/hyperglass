"""
Defines models for VRF config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List
from typing import Dict

# Third Party Imports
from pydantic import BaseSettings
from pydantic import IPvAnyNetwork
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import clean_name
from hyperglass.exceptions import ConfigInvalid


class Vrf(BaseSettings):
    """Model for per VRF/afi config in devices.yaml"""

    display_name: str
    ipv4: bool = True
    ipv6: bool = True
    access_list: List[Dict[str, IPvAnyNetwork]] = [
        {"allow": "0.0.0.0/0"},
        {"allow": "::/0"},
    ]

    @validator("access_list", whole=True, always=True)
    def validate_action(cls, value):
        allowed_actions = ("allow", "deny")
        for li in value:
            for action, network in li.items():
                if action not in allowed_actions:
                    raise ConfigInvalid(
                        field=action,
                        error_msg=(
                            "Access List Entries must be formatted as "
                            '"- action: network" (list of dictionaries with the action '
                            "as the key, and the network as the value), e.g. "
                            '"- deny: 192.0.2.0/24 or "- allow: 2001:db8::/32".'
                        ),
                    )
        return value


class Vrfs(BaseSettings):
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

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True
