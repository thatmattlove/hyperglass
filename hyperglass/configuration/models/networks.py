"""
Defines models for Networks config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import clean_name


class Network(HyperglassModel):
    """Model for per-network/asn config in devices.yaml"""

    name: str
    display_name: str


class Networks(HyperglassModel):
    """Base model for networks class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the credentials class.
        """
        obj = Networks()
        networks = {}
        for (netname, params) in input_params.items():
            netname = clean_name(netname)
            setattr(Networks, netname, Network(**params))
            networks.update({netname: Network(**params).dict()})
        Networks.networks = networks
        return obj
