"""Validate credential configuration variables."""

# Third Party
from pydantic import SecretStr, StrictStr

# Project
from hyperglass.models import HyperglassModel


class Credential(HyperglassModel):
    """Model for per-credential config in devices.yaml."""

    username: StrictStr
    password: SecretStr
