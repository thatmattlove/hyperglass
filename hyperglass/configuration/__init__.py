"""
Imports configuration varibles from configuration files and returns
default values if undefined.
"""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
import logzero
import stackprinter
import yaml
from logzero import logger as log
from pydantic import ValidationError

# Project Imports
from hyperglass.configuration.models import (
    params as _params,
    commands as _commands,
    routers as _routers,
    proxies as _proxies,
    networks as _networks,
    vrfs as _vrfs,
    credentials as _credentials,
)
from hyperglass.exceptions import ConfigError, ConfigInvalid, ConfigMissing

# Stackprinter Configuration
stack = stackprinter.set_excepthook()

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
        log.info(f"Found commands: {user_commands}")
except FileNotFoundError:
    user_commands = None
    log.info(
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
    raise ConfigError(error_msg=yaml_error) from None

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

    devices = _routers.Routers.import_params(user_devices.get("router", dict()))
    credentials = _credentials.Credentials.import_params(
        user_devices.get("credential", dict())
    )
    proxies = _proxies.Proxies.import_params(user_devices.get("proxy", dict()))
    imported_networks = _networks.Networks.import_params(
        user_devices.get("network", dict())
    )
    vrfs = _vrfs.Vrfs.import_params(user_devices.get("vrf", dict()))


except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

# Validate that VRFs configured on a device are actually defined
for dev in devices.hostnames:
    dev_cls = getattr(devices, dev)
    display_vrfs = []
    for vrf in getattr(dev_cls, "_vrfs"):
        if vrf not in vrfs._all:
            raise ConfigInvalid(
                field=vrf, error_msg=f"{vrf} is not in configured VRFs: {vrfs._all}"
            )
        vrf_attr = getattr(vrfs, vrf)
        display_vrfs.append(vrf_attr.display_name)
    devices.routers[dev]["display_vrfs"] = display_vrfs
    setattr(dev_cls, "display_vrfs", display_vrfs)


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


class Networks:
    def __init__(self):
        self.routers = devices.routers
        self.networks = imported_networks.networks

    def networks_verbose(self):
        locations_dict = {}
        for (router, router_params) in self.routers.items():
            for (netname, net_params) in self.networks.items():
                if router_params["network"] == netname:
                    net_display = net_params["display_name"]
                    if net_display in locations_dict:
                        locations_dict[net_display].append(
                            {
                                "location": router_params["location"],
                                "hostname": router,
                                "display_name": router_params["display_name"],
                                "vrfs": router_params["vrfs"],
                            }
                        )
                    elif net_display not in locations_dict:
                        locations_dict[net_display] = [
                            {
                                "location": router_params["location"],
                                "hostname": router,
                                "display_name": router_params["display_name"],
                                "vrfs": router_params["vrfs"],
                            }
                        ]
        if not locations_dict:
            raise ConfigError(error_msg="Unable to build network to device mapping")
        return locations_dict

    def networks_display(self):
        locations_dict = {}
        for (router, router_params) in self.routers.items():
            for (netname, net_params) in self.networks.items():
                if router_params["network"] == netname:
                    net_display = net_params["display_name"]
                    if net_display in locations_dict:
                        locations_dict[net_display].append(
                            router_params["display_name"]
                        )
                    elif net_display not in locations_dict:
                        locations_dict[net_display] = [router_params["display_name"]]
        if not locations_dict:
            raise ConfigError(error_msg="Unable to build network to device mapping")
        return [
            {"network_name": netname, "location_names": display_name}
            for (netname, display_name) in locations_dict.items()
        ]

    def frontend_networks(self):
        frontend_dict = {}
        for (router, router_params) in self.routers.items():
            for (netname, net_params) in self.networks.items():
                if router_params["network"] == netname:
                    net_display = net_params["display_name"]
                    if net_display in frontend_dict:
                        frontend_dict[net_display].update(
                            {
                                router: {
                                    "location": router_params["location"],
                                    "display_name": router_params["display_name"],
                                    "vrfs": router_params["display_vrfs"],
                                }
                            }
                        )
                    elif net_display not in frontend_dict:
                        frontend_dict[net_display] = {
                            router: {
                                "location": router_params["location"],
                                "display_name": router_params["display_name"],
                                "vrfs": router_params["display_vrfs"],
                            }
                        }
        if not frontend_dict:
            raise ConfigError(error_msg="Unable to build network to device mapping")
        return frontend_dict


net = Networks()
networks = net.networks_verbose()
display_networks = net.networks_display()
frontend_networks = net.frontend_networks()

frontend_fields = {
    "general": {"debug", "request_timeout"},
    "branding": {"text"},
    "messages": ...,
}
frontend_params = params.dict(include=frontend_fields)
