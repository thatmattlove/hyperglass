"""Validation model for cache config."""


# Local
from ..main import HyperglassModel


class Cache(HyperglassModel):
    """Public cache parameters."""

    timeout: int = 120
    show_text: bool = True
