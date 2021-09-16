"""Import configuration files and returns default values if undefined."""

# Standard Library
from typing import Dict, List, Generator
from pathlib import Path

# Third Party
import yaml
from pydantic import ValidationError

# Project
from hyperglass.log import log, enable_file_logging, enable_syslog_logging
from hyperglass.util import set_cache_env
from hyperglass.defaults import CREDIT
from hyperglass.settings import Settings
from hyperglass.constants import PARSED_RESPONSE_FIELDS, __version__
from hyperglass.models.ui import UIParameters
from hyperglass.util.files import check_path
from hyperglass.exceptions.private import ConfigError, ConfigMissing
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices
from hyperglass.models.commands.generic import Directive

# Local
from .markdown import get_markdown
from .validation import validate_config

CONFIG_PATH = Settings.app_path
log.info("Configuration directory: {d!s}", d=CONFIG_PATH)

# Project Directories
WORKING_DIR = Path(__file__).resolve().parent
CONFIG_FILES = (
    ("hyperglass.yaml", False),
    ("devices.yaml", True),
    ("commands.yaml", False),
)


def _check_config_files(directory: Path):
    """Verify config files exist and are readable."""

    files = ()

    for file in CONFIG_FILES:
        file_name, required = file
        file_path = directory / file_name

        checked = check_path(file_path)

        if checked is None and required:
            raise ConfigMissing(missing_item=str(file_path))

        if checked is None and not required:
            log.warning(
                "'{f}' was not found, but is not required to run hyperglass. "
                + "Defaults will be used.",
                f=str(file_path),
            )
        files += (checked,)

    return files


CONFIG_MAIN, CONFIG_DEVICES, CONFIG_COMMANDS = _check_config_files(CONFIG_PATH)


def _config_required(config_path: Path) -> Dict:
    try:
        with config_path.open("r") as cf:
            config = yaml.safe_load(cf)

    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(message="Error reading YAML file: '{e}'", e=yaml_error)

    if config is None:
        raise ConfigMissing(missing_item=config_path.name)

    return config


def _config_optional(config_path: Path) -> Dict:

    config = {}

    if config_path is None:
        return config

    else:
        try:
            with config_path.open("r") as cf:
                config = yaml.safe_load(cf) or {}

        except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
            raise ConfigError(message="Error reading YAML file: '{e}'", e=yaml_error)

    return config


def _get_commands(data: Dict) -> List[Directive]:
    commands = []
    for name, command in data.items():
        try:
            commands.append(Directive(id=name, **command))
        except ValidationError as err:
            raise ConfigError(
                message="Validation error in command '{c}': '{e}'", c=name, e=err
            ) from err
    return commands


def _device_commands(device: Dict, directives: List[Directive]) -> Generator[Directive, None, None]:
    device_commands = device.get("commands", [])
    for directive in directives:
        if directive.id in device_commands:
            yield directive


def _get_devices(data: List[Dict], directives: List[Directive]) -> Devices:
    for device in data:
        device_commands = list(_device_commands(device, directives))
        device["commands"] = device_commands
    return Devices(data)


user_config = _config_optional(CONFIG_MAIN)

# Read raw debug value from config to enable debugging quickly.

# Map imported user configuration to expected schema.
log.debug("Unvalidated configuration from {}: {}", CONFIG_MAIN, user_config)
params = validate_config(config=user_config, importer=Params)

# Map imported user commands to expected schema.
_user_commands = _config_optional(CONFIG_COMMANDS)
log.debug("Unvalidated commands from {}: {}", CONFIG_COMMANDS, _user_commands)
commands = _get_commands(_user_commands)

# Map imported user devices to expected schema.
_user_devices = _config_required(CONFIG_DEVICES)
log.debug("Unvalidated devices from {}: {}", CONFIG_DEVICES, _user_devices)
devices: Devices = _get_devices(_user_devices.get("routers", []), commands)

# Set cache configurations to environment variables, so they can be
# used without importing this module (Gunicorn, etc).
set_cache_env(db=params.cache.database, host=params.cache.host, port=params.cache.port)

# Set up file logging once configuration parameters are initialized.
enable_file_logging(
    logger=log,
    log_directory=params.logging.directory,
    log_format=params.logging.format,
    log_max_size=params.logging.max_size,
)

# Set up syslog logging if enabled.
if params.logging.syslog is not None and params.logging.syslog.enable:
    enable_syslog_logging(
        logger=log, syslog_host=params.logging.syslog.host, syslog_port=params.logging.syslog.port,
    )

if params.logging.http is not None and params.logging.http.enable:
    log.debug("HTTP logging is enabled")

# Perform post-config initialization string formatting or other
# functions that require access to other config levels. E.g.,
# something in 'params.web.text' needs to be formatted with a value
# from params.
try:
    params.web.text.subtitle = params.web.text.subtitle.format(
        **params.dict(exclude={"web", "queries", "messages"})
    )

    # If keywords are unmodified (default), add the org name &
    # site_title.
    if Params().site_keywords == params.site_keywords:
        params.site_keywords = sorted({*params.site_keywords, params.org_name, params.site_title})

except KeyError:
    pass


content_greeting = get_markdown(
    config_path=params.web.greeting, default="", params={"title": params.web.greeting.title},
)


content_credit = CREDIT.format(version=__version__)

_ui_params = params.frontend()
_ui_params["web"]["logo"]["light_format"] = params.web.logo.light.suffix
_ui_params["web"]["logo"]["dark_format"] = params.web.logo.dark.suffix

ui_params = UIParameters(
    **_ui_params,
    version=__version__,
    networks=devices.networks(params),
    parsed_data_fields=PARSED_RESPONSE_FIELDS,
    content={"credit": content_credit, "greeting": content_greeting},
)

URL_PROD = "/api/"
