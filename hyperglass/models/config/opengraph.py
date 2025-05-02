"""Validate OpenGraph Configuration Parameters."""

# Standard Library
from pathlib import Path

# Third Party
from pydantic import FilePath, field_validator

# Local
from ..main import HyperglassModel

DEFAULT_IMAGES = Path(__file__).parent.parent.parent / "images"


class OpenGraph(HyperglassModel):
    """Validation model for params.opengraph."""

    image: FilePath = DEFAULT_IMAGES / "hyperglass-opengraph.jpg"

    @field_validator("image")
    def validate_opengraph(cls, value):
        """Ensure the opengraph image is a supported format."""
        supported_extensions = (".jpg", ".jpeg", ".png")
        if value is not None and value.suffix not in supported_extensions:
            raise ValueError(
                "OpenGraph image must be one of {e}".format(e=", ".join(supported_extensions))
            )

        return value
