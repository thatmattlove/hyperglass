"""Validate credential configuration variables."""

# Third Party
from pydantic import SecretStr, StrictStr

# Local
from ..main import HyperglassModel


class Credential(HyperglassModel):
    """Model for per-credential config in devices.yaml."""

    username: StrictStr
    password: SecretStr
