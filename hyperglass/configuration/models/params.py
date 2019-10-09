"""
Defines models for all Params variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models.branding import Branding
from hyperglass.configuration.models.features import Features
from hyperglass.configuration.models.general import General
from hyperglass.configuration.models.messages import Messages


class Params(HyperglassModel):
    """Base model for params"""

    general: General = General()
    features: Features = Features()
    branding: Branding = Branding()
    messages: Messages = Messages()
