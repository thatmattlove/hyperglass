"""Validate network configuration variables."""

# Third Party
from pydantic import Field, StrictStr

# Local
from ..main import HyperglassModel


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
