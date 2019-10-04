"""
Utility Functions for Pydantic Models
"""

import re
from pydantic import BaseSettings


def clean_name(_name):
    """
    Converts any "desirable" seperators to underscore, then
    removes all characters that are unsupported in Python class
    variable names. Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


class HyperglassModel(BaseSettings):
    """Base model for all hyperglass configuration models"""

    pass

    class Config:
        """Default pydantic configuration"""

        validate_all = True
        extra = "forbid"
        validate_assignment = True
