"""Validate SSL configuration variables."""

# Third Party Imports
from pydantic import FilePath
from pydantic import StrictBool

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Ssl(HyperglassModel):
    """Validate SSL config parameters."""

    enable: StrictBool = True
    cert: FilePath
