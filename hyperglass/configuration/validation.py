"""Post-Validation Validation.

Some validations need to occur across multiple config files.
"""
# Standard Library
from typing import Dict, List, Union, Callable

# Third Party
from pydantic import ValidationError

# Project
from hyperglass.log import log
from hyperglass.models import HyperglassModel
from hyperglass.constants import TRANSPORT_REST, SUPPORTED_STRUCTURED_OUTPUT
from hyperglass.exceptions import ConfigError, ConfigInvalid
from hyperglass.models.commands import Commands


def validate_nos_commands(all_nos: List[str], commands: Commands) -> bool:
    """Ensure defined devices have associated commands."""
    custom_commands = commands.dict().keys()

    for nos in all_nos:
        valid = False
        if nos in (*SUPPORTED_STRUCTURED_OUTPUT, *TRANSPORT_REST, *custom_commands):
            valid = True

        if not valid:
            raise ConfigError(
                '"{nos}" is used on a device, '
                + 'but no command profile for "{nos}" is defined.',
                nos=nos,
            )

    return True


def validate_config(config: Union[Dict, List], importer: Callable) -> HyperglassModel:
    """Validate a config dict against a model."""
    validated = None
    try:
        if isinstance(config, Dict):
            validated = importer(**config)
        elif isinstance(config, List):
            validated = importer(config)
    except ValidationError as err:
        log.error(str(err))
        raise ConfigInvalid(err.errors()) from None

    return validated
