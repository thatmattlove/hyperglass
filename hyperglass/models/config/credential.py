"""Validate credential configuration variables."""

# Standard Library
from typing import Optional

# Third Party
from pydantic import FilePath, SecretStr, StrictStr, constr, root_validator

# Local
from ..main import HyperglassModelExtra

Methods = constr(regex=r"(password|unencrypted_key|encrypted_key)")


class Credential(HyperglassModelExtra):
    """Model for per-credential config in devices.yaml."""

    username: StrictStr
    password: Optional[SecretStr]
    key: Optional[FilePath]

    @root_validator
    def validate_credential(cls, values):
        """Ensure either a password or an SSH key is set."""
        if values["key"] is None and values["password"] is None:
            raise ValueError(
                "Either a password or an SSH key must be specified for user '{}'".format(
                    values["username"]
                )
            )
        return values

    def __init__(self, **kwargs):
        """Set private attribute _method based on validated model."""
        super().__init__(**kwargs)
        self._method = None
        if self.password is not None and self.key is not None:
            self._method = "encrypted_key"
        elif self.password is None:
            self._method = "unencrypted_key"
        elif self.key is None:
            self._method = "password"
