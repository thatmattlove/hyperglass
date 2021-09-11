"""Post-Validation Validation.

Some validations need to occur across multiple config files.
"""
# Standard Library
from typing import Any, Dict, List, Union, TypeVar

# Third Party
from pydantic import ValidationError

# Project
from hyperglass.exceptions.private import ConfigInvalid

Importer = TypeVar("Importer")


def validate_config(
    config: Union[Dict[str, Any], List[Any]], importer: Importer
) -> Importer:
    """Validate a config dict against a model."""
    validated = None
    try:
        if isinstance(config, Dict):
            validated = importer(**config)
        elif isinstance(config, List):
            validated = importer(config)
    except ValidationError as err:
        raise ConfigInvalid(errors=err.errors()) from None

    return validated
