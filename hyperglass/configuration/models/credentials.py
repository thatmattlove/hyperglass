"""
Defines models for Credential config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Third Party Imports
from pydantic import BaseSettings
from pydantic import SecretStr

# Project Imports
from hyperglass.configuration.models._utils import clean_name


class Credential(BaseSettings):
    """Model for per-credential config in devices.yaml"""

    username: str
    password: SecretStr


class Credentials(BaseSettings):
    """Base model for credentials class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the credentials class.
        """
        obj = Credentials()
        for (credname, params) in input_params.items():
            cred = clean_name(credname)
            setattr(Credentials, cred, Credential(**params))
        return obj

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True
