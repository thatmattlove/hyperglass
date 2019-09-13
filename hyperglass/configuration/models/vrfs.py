"""
Defines models for VRF config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseSettings

# Project Imports
from hyperglass.configuration.models._utils import clean_name


class Vrf(BaseSettings):
    """Model for per VRF/afi config in devices.yaml"""

    display_name: str
    label: str
    afis: List[str]


class Vrfs(BaseSettings):
    """Base model for vrfs class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from VRF names, dynamically sets attributes for
        the Vrfs class.
        """
        vrfs: Vrf = {
            "default": {
                "display_name": "Default",
                "label": "default",
                "afis": ["ipv4, ipv6"],
            }
        }
        labels: List[str] = ["default"]
        _all: List[str] = ["default"]

        for (vrf_key, params) in input_params.items():
            vrf = clean_name(vrf_key)
            vrf_params = Vrf(**params)
            vrfs.update({vrf: vrf_params.dict()})
            labels.append(params.get("label"))
            _all.append(vrf_key)
        for (vrf_key, params) in vrfs.items():
            setattr(Vrfs, vrf_key, params)

        labels: List[str] = list(set(labels))
        _all: List[str] = list(set(_all))
        Vrfs.vrfs = vrfs
        Vrfs.labels = labels
        Vrfs._all = _all
        return Vrfs()

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True
