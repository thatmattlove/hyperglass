"""Validate logging configuration."""

# Standard Library
from typing import Optional
from pathlib import Path

# Third Party
from pydantic import ByteSize, StrictInt, StrictStr, StrictBool, DirectoryPath, constr

# Project
from hyperglass.configuration.models._utils import HyperglassModel


class Syslog(HyperglassModel):
    """Validation model for syslog configuration."""

    enable: StrictBool = True
    host: StrictStr
    port: StrictInt = 514


class Logging(HyperglassModel):
    """Validation model for logging configuration."""

    directory: DirectoryPath = Path("/tmp")  # noqa: S108
    format: constr(regex=r"(text|json)") = "text"
    syslog: Optional[Syslog]
    max_size: ByteSize = "50MB"
