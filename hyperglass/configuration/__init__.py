"""
Imports configuration varibles from configuration files and returns
default values if undefined.
"""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
import logzero
import yaml
from logzero import logger
from pydantic import ValidationError

# Project Imports
from hyperglass.configuration import models
from hyperglass.exceptions import ConfigError

# Project Directories
working_dir = Path(__file__).resolve().parent

# Import main hyperglass configuration file
try:
    with open(working_dir.joinpath("hyperglass.yaml")) as config_yaml:
        user_config = yaml.safe_load(config_yaml)
except FileNotFoundError as no_config_error:
    user_config = None
    logger.error(f"{no_config_error} - Default configuration will be used")
# Import device commands file
try:
    with open(working_dir.joinpath("commands.yaml")) as commands_yaml:
        user_commands = yaml.safe_load(commands_yaml)
except FileNotFoundError:
    user_commands = None
    logger.info(
        (
            f'No commands found in {working_dir.joinpath("commands.yaml")}. '
            "Defaults will be used."
        )
    )
# Import device configuration file
try:
    with open(working_dir.joinpath("devices.yaml")) as devices_yaml:
        user_devices = yaml.safe_load(devices_yaml)
except FileNotFoundError as no_devices_error:
    logger.error(no_devices_error)
    raise ConfigError(
        (
            f'"{working_dir.joinpath("devices.yaml")}" not found. '
            "Devices are required to start hyperglass, please consult "
            "the installation documentation."
        )
    )

# Map imported user config files to expected schema:
try:
    if user_config:
        params = models.Params(**user_config)
    elif not user_config:
        params = models.Params()
    if user_commands:
        commands = models.Commands.import_params(user_commands)
    elif not user_commands:
        commands = models.Commands()
    devices = models.Routers.import_params(user_devices["router"])
    credentials = models.Credentials.import_params(user_devices["credential"])
    proxies = models.Proxies.import_params(user_devices["proxy"])
    networks = models.Networks.import_params(user_devices["network"])
except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigError(
            f'The value of {error["loc"][0]} field is invalid: {error["msg"]} '
        )

# Logzero Configuration
log_level = 20
if params.general.debug:
    log_level = 10
log_format = (
    "%(color)s[%(asctime)s.%(msecs)03d %(module)s:%(funcName)s:%(lineno)d "
    "%(levelname)s]%(end_color)s %(message)s"
)
date_format = "%Y-%m-%d %H:%M:%S"
logzero_formatter = logzero.LogFormatter(fmt=log_format, datefmt=date_format)
logzero_config = logzero.setup_default_logger(
    formatter=logzero_formatter, level=log_level
)
