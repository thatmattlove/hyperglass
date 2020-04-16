"""Validate credential configuration variables."""

# Third Party
from pydantic import SecretStr, StrictStr

# Project
from hyperglass.util import clean_name
from hyperglass.models import HyperglassModel


class Credential(HyperglassModel):
    """Model for per-credential config in devices.yaml."""

    username: StrictStr
    password: SecretStr


class Credentials(HyperglassModel):
    """Base model for credentials class."""

    @classmethod
    def import_params(cls, input_params):
        """Import credentials with corrected field names.

        Arguments:
            input_params {dict} -- Credential definition

        Returns:
            {object} -- Validated credential object
        """
        obj = Credentials()
        for (credname, params) in input_params.items():
            cred = clean_name(credname)
            setattr(Credentials, cred, Credential(**params))
        return obj
