"""Validate credential configuration variables."""

# Standard Library
import typing as t

# Third Party
from pydantic import FilePath, SecretStr, model_validator

# Local
from ..main import HyperglassModel

AuthMethod = t.Literal["password", "unencrypted_key", "encrypted_key"]


class Credential(HyperglassModel, extra="allow"):
    """Model for per-credential config in devices.yaml."""

    username: str
    password: t.Optional[SecretStr] = None
    key: t.Optional[FilePath] = None
    _method: t.Optional[AuthMethod] = None

    @model_validator(mode="after")
    def validate_credential(cls, data: "Credential"):
        """Ensure either a password or an SSH key is set."""
        if data.key is None and data.password is None:
            raise ValueError(
                "Either a password or an SSH key must be specified for user '{}'".format(
                    data.username
                )
            )
        return data

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
