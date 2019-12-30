"""Import configuration files and returns default values if undefined."""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
import yaml
from pydantic import ValidationError

# Project Imports
from hyperglass.configuration.models import commands as _commands
from hyperglass.configuration.models import params as _params
from hyperglass.configuration.models import routers as _routers
from hyperglass.constants import LOG_HANDLER
from hyperglass.constants import LOG_LEVELS
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import ConfigInvalid
from hyperglass.exceptions import ConfigMissing
from hyperglass.util import log

# Project Directories
working_dir = Path(__file__).resolve().parent

# Import main hyperglass configuration file
try:
    with open(working_dir.joinpath("hyperglass.yaml")) as config_yaml:
        user_config = yaml.safe_load(config_yaml)
except FileNotFoundError as no_config_error:
    user_config = None
    log.error(f"{no_config_error} - Default configuration will be used")

# Import commands file
try:
    with open(working_dir.joinpath("commands.yaml")) as commands_yaml:
        user_commands = yaml.safe_load(commands_yaml)
        log.debug(f"Found commands: {user_commands}")
except FileNotFoundError:
    user_commands = None
    log.debug(
        (
            f'No commands found in {working_dir.joinpath("commands.yaml")}. '
            "Defaults will be used."
        )
    )
except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
    raise ConfigError(error_msg=yaml_error) from None

# Import device configuration file
try:
    with open(working_dir.joinpath("devices.yaml")) as devices_yaml:
        user_devices = yaml.safe_load(devices_yaml)
except FileNotFoundError as no_devices_error:
    log.error(no_devices_error)
    raise ConfigMissing(
        missing_item=str(working_dir.joinpath("devices.yaml"))
    ) from None
except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
    raise ConfigError(str(yaml_error)) from None

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

    devices = _routers.Routers._import(user_devices.get("routers", dict()))


except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )


# Logging Config
LOG_LEVEL = "INFO"
if params.general.debug:
    LOG_LEVEL = "DEBUG"
    LOG_HANDLER["level"] = LOG_LEVEL
    log.remove()
    log.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)

log.debug("Debugging Enabled")


def build_frontend_networks():
    """
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


def build_frontend_devices():
    """
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


def build_networks():
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


networks = build_networks()
frontend_networks = build_frontend_networks()
frontend_devices = build_frontend_devices()

frontend_fields = {
    "general": {"debug", "request_timeout"},
    "branding": {"text"},
    "messages": ...,
}
frontend_params = params.dict(include=frontend_fields)
