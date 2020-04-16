"""Validate OpenGraph Configuration Parameters."""

# Standard Library
import os
from typing import Optional
from pathlib import Path

# Third Party
import PIL.Image as PilImage
from pydantic import StrictInt, StrictStr, root_validator

# Project
from hyperglass.models import HyperglassModel
from hyperglass.configuration.models._utils import validate_image

CONFIG_PATH = Path(os.environ["hyperglass_directory"])


class OpenGraph(HyperglassModel):
    """Validation model for params.opengraph."""

    width: Optional[StrictInt]
    height: Optional[StrictInt]
    image: Optional[StrictStr]

    @root_validator
    def validate_opengraph(cls, values):
        """Set default opengraph image location.

        Arguments:
            value {FilePath} -- Path to opengraph image file.

        Returns:
            {Path} -- Opengraph image file path object
        """
        supported_extensions = (".jpg", ".jpeg", ".png")
        if (
            values["image"] is not None
            and Path(values["image"]).suffix not in supported_extensions
        ):
            raise ValueError(
                "OpenGraph image must be one of {e}".format(
                    e=", ".join(supported_extensions)
                )
            )
        if values["image"] is None:
            values["image"] = "images/hyperglass-opengraph.png"

        values["image"] = validate_image(values["image"])

        image_file = CONFIG_PATH / "static" / values["image"]

        with PilImage.open(image_file) as img:
            width, height = img.size
            if values["width"] is None:
                values["width"] = width
            if values["height"] is None:
                values["height"] = height

        return values

    class Config:
        """Pydantic model configuration."""

        title = "OpenGraph"
        description = "OpenGraph configuration parameters"
        fields = {
            "width": {
                "title": "Width",
                "description": "Width of OpenGraph image. If unset, the width will be automatically derived by reading the image file.",
            },
            "height": {
                "title": "Height",
                "description": "Height of OpenGraph image. If unset, the height will be automatically derived by reading the image file.",
            },
            "image": {
                "title": "Image File",
                "description": "Valid path to a JPG or PNG file to use as the OpenGraph image.",
            },
        }
        schema_extra = {"level": 3}
