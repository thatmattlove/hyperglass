"""Validate network configuration variables."""

# Third Party
from pydantic import Field, StrictStr

# Project
from hyperglass.util import clean_name
from hyperglass.models import HyperglassModel


class Network(HyperglassModel):
    """Validation Model for per-network/asn config in devices.yaml."""

    name: StrictStr = Field(
        ...,
        title="Network Name",
        description="Internal name of the device's primary network.",
    )
    display_name: StrictStr = Field(
        ...,
        title="Network Display Name",
        description="Display name of the device's primary network.",
    )


class Networks(HyperglassModel):
    """Base model for networks class."""

    @classmethod
    def import_params(cls, input_params):
        """Import loaded YAML, initialize per-network definitions.

        Remove unsupported characters from network names, dynamically
        set attributes for the networks class. Add cls.networks
        attribute so network objects can be accessed inside a dict.

        Arguments:
            input_params {dict} -- Unvalidated network definitions

        Returns:
            {object} -- Validated networks object
        """
        obj = Networks()
        networks = {}
        for (netname, params) in input_params.items():
            netname = clean_name(netname)
            setattr(Networks, netname, Network(**params))
            networks.update({netname: Network(**params).dict()})
        Networks.networks = networks
        return obj
