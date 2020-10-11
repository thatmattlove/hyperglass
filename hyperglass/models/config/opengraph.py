"""Validate OpenGraph Configuration Parameters."""

# Standard Library
import os
from pathlib import Path

# Third Party
from pydantic import FilePath, validator

# Local
from ..main import HyperglassModel

CONFIG_PATH = Path(os.environ["hyperglass_directory"])
DEFAULT_IMAGES = Path(__file__).parent.parent.parent / "images"


class OpenGraph(HyperglassModel):
    """Validation model for params.opengraph."""

    image: FilePath = DEFAULT_IMAGES / "hyperglass-opengraph.jpg"

    @validator("image")
    def validate_opengraph(cls, value):
        """Ensure the opengraph image is a supported format.

        Arguments:
            value {FilePath} -- Path to opengraph image file.

        Returns:
            {Path} -- Opengraph image file path object
        """
        supported_extensions = (".jpg", ".jpeg", ".png")
        if value is not None and value.suffix not in supported_extensions:
            raise ValueError(
                "OpenGraph image must be one of {e}".format(
                    e=", ".join(supported_extensions)
                )
            )

        return value
