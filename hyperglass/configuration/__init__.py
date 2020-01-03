"""Import configuration files and returns default values if undefined."""

# Standard Library Imports
import asyncio
from pathlib import Path

# Third Party Imports
import yaml
from aiofile import AIOFile
from pydantic import ValidationError

# Project Imports
from hyperglass.configuration.models import commands as _commands
from hyperglass.configuration.models import params as _params
from hyperglass.configuration.models import routers as _routers
from hyperglass.constants import LOG_HANDLER
from hyperglass.constants import LOG_HANDLER_FILE
from hyperglass.constants import LOG_LEVELS
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import ConfigInvalid
from hyperglass.exceptions import ConfigMissing
from hyperglass.util import log

# Project Directories
working_dir = Path(__file__).resolve().parent

# Config Files
config_file_main = working_dir / "hyperglass.yaml"
config_file_devices = working_dir / "devices.yaml"
config_file_commands = working_dir / "commands.yaml"


def _set_log_level(debug, log_file=None):
    """Set log level based on debug state.

    Arguments:
        debug {bool} -- Debug state from config file

    Returns:
        {bool} -- True
    """
    stdout_handler = LOG_HANDLER.copy()
    file_handler = LOG_HANDLER_FILE.copy()

    if debug:
        log_level = "DEBUG"
        stdout_handler["level"] = log_level
        file_handler["level"] = log_level

    if log_file is not None:
        file_handler.update({"sink": log_file})
        log_handlers = [stdout_handler, file_handler]
    else:
        log_handlers = [stdout_handler]

    log.remove()
    log.configure(handlers=log_handlers, levels=LOG_LEVELS)
    if debug:
        log.debug("Debugging enabled")
    return True


async def _config_main():
    """Open main config file and load YAML to dict.

    Returns:
        {dict} -- Main config file
    """
    try:
        async with AIOFile(config_file_main, "r") as cf:
            raw = await cf.read()
            config = yaml.safe_load(raw)
    except FileNotFoundError as nf:
        config = None
        log.warning(f"{str(nf)} - Default configuration will be used")
    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(error_msg=str(yaml_error)) from None
    return config


async def _config_commands():
    """Open commands config file and load YAML to dict.

    Returns:
        {dict} -- Commands config file
    """
    try:
        async with AIOFile(config_file_commands, "r") as cf:
            raw = await cf.read()
            config = yaml.safe_load(raw)
            log.debug(f"Unvalidated commands: {config}")
    except FileNotFoundError as nf:
        config = None
        log.warning(f"{str(nf)} - Default commands will be used.")
    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(error_msg=str(yaml_error)) from None
    return config


async def _config_devices():
    """Open devices config file and load YAML to dict.

    Returns:
        {dict} -- Devices config file
    """
    try:
        async with AIOFile(config_file_devices, "r") as cf:
            raw = await cf.read()
            config = yaml.safe_load(raw)
            log.debug(f"Unvalidated device config: {config}")
    except FileNotFoundError:
        raise ConfigMissing(missing_item=str(config_file_devices)) from None
    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(error_msg=str(yaml_error)) from None
    return config


user_config = asyncio.run(_config_main())

# Logging Config
try:
    _debug = user_config["general"]["debug"]
except KeyError:
    _debug = True

# Read raw debug value from config to enable debugging quickly needed.
_set_log_level(_debug)

user_commands = asyncio.run(_config_commands())
user_devices = asyncio.run(_config_devices())

# Map imported user config files to expected schema:
try:
    if user_config:
        params = _params.Params(**user_config)
    elif not user_config:
        params = _params.Params()

    if user_commands:
        commands = _commands.Commands.import_params(user_commands)
    elif not user_commands:
        commands = _commands.Commands()

    devices = _routers.Routers._import(user_devices.get("routers", {}))

except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

# Re-evaluate debug state after config is validated
_set_log_level(params.general.debug, params.general.log_file)


def _build_frontend_networks():
    """Build filtered JSON structure of networks for frontend.

    Schema:
    {
        "device.network.display_name": {
            "device.name": {
                "location": "device.location",
                "display_name": "device.display_name",
                "vrfs": [
                    "Global",
                    "vrf.display_name"
                ]
            }
        }
    }

    Raises:
        ConfigError: Raised if parsing/building error occurs.

    Returns:
        {dict} -- Frontend networks
    """
    frontend_dict = {}
    for device in devices.routers:
        if device.network.display_name in frontend_dict:
            frontend_dict[device.network.display_name].update(
                {
                    device.name: {
                        "location": device.location,
                        "display_name": device.network.display_name,
                        "vrfs": [vrf.display_name for vrf in device.vrfs],
                    }
                }
            )
        elif device.network.display_name not in frontend_dict:
            frontend_dict[device.network.display_name] = {
                device.name: {
                    "location": device.location,
                    "display_name": device.network.display_name,
                    "vrfs": [vrf.display_name for vrf in device.vrfs],
                }
            }
    frontend_dict["default_vrf"] = devices.default_vrf
    if not frontend_dict:
        raise ConfigError(error_msg="Unable to build network to device mapping")
    return frontend_dict


def _build_frontend_devices():
    """Build filtered JSON structure of devices for frontend.

    Schema:
    {
        "device.name": {
            "location": "device.location",
            "display_name": "device.display_name",
            "vrfs": [
                "Global",
                "vrf.display_name"
            ]
        }
    }

    Raises:
        ConfigError: Raised if parsing/building error occurs.

    Returns:
        {dict} -- Frontend devices
    """
    frontend_dict = {}
    for device in devices.routers:
        if device.name in frontend_dict:
            frontend_dict[device.name].update(
                {
                    "location": device.location,
                    "network": device.network.display_name,
                    "display_name": device.display_name,
                    "vrfs": [vrf.display_name for vrf in device.vrfs],
                }
            )
        elif device.name not in frontend_dict:
            frontend_dict[device.name] = {
                "location": device.location,
                "network": device.network.display_name,
                "display_name": device.display_name,
                "vrfs": [vrf.display_name for vrf in device.vrfs],
            }
    if not frontend_dict:
        raise ConfigError(error_msg="Unable to build network to device mapping")
    return frontend_dict


def _build_networks():
    """Build filtered JSON Structure of networks & devices for Jinja templates.

    Raises:
        ConfigError: Raised if parsing/building error occurs.

    Returns:
        {dict} -- Networks & devices
    """
    networks_dict = {}
    for device in devices.routers:
        if device.network.display_name in networks_dict:
            networks_dict[device.network.display_name].append(
                {
                    "location": device.location,
                    "hostname": device.name,
                    "display_name": device.display_name,
                    "vrfs": [vrf.name for vrf in device.vrfs],
                }
            )
        elif device.network.display_name not in networks_dict:
            networks_dict[device.network.display_name] = [
                {
                    "location": device.location,
                    "hostname": device.name,
                    "display_name": device.display_name,
                    "vrfs": [vrf.name for vrf in device.vrfs],
                }
            ]
    if not networks_dict:
        raise ConfigError(error_msg="Unable to build network to device mapping")
    return networks_dict


_frontend_fields = {
    "general": {"debug", "request_timeout"},
    "branding": {"text"},
    "messages": ...,
}
frontend_params = params.dict(include=_frontend_fields)
networks = _build_networks()
frontend_networks = _build_frontend_networks()
frontend_devices = _build_frontend_devices()
