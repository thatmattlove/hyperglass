# Standard Library Imports
from pathlib import Path
from typing import Optional

# Third Party Imports
import PIL.Image as PilImage
from pydantic import FilePath
from pydantic import StrictInt
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class OpenGraph(HyperglassModel):
    """Validation model for params.general.opengraph."""

    width: Optional[StrictInt]
    height: Optional[StrictInt]
    image: Optional[FilePath]

    @validator("image")
    def validate_image(cls, value, values):
        """Set default opengraph image location.

        Arguments:
            value {FilePath} -- Path to opengraph image file.

        Returns:
            {Path} -- Opengraph image file path object
        """
        if value is None:
            value = (
                Path(__file__).parent.parent.parent
                / "static/ui/images/hyperglass-opengraph.png"
            )
        with PilImage.open(value) as img:
            width, height = img.size
            values["width"] = width
            values["height"] = height

        return "".join(str(value).split("static")[1::])
