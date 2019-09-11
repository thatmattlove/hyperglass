"""
Utility Functions for Pydantic Models
"""

import re


def clean_name(_name):
    """
    Converts any "desirable" seperators to underscore, then
    removes all characters that are unsupported in Python class
    variable names. Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()
