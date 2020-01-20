# Third Party Imports
from pydantic import StrictBool
from pydantic import constr

# Project Imports
from hyperglass.configuration.models._utils import AnyUri
from hyperglass.configuration.models._utils import HyperglassModel


class Docs(HyperglassModel):
    """Validation model for params.general.docs."""

    enable: StrictBool = True
    mode: constr(regex=r"(swagger|redoc)") = "swagger"
    uri: AnyUri = "/docs"
