"""Import configuration files and returns default values if undefined."""

# Standard Library Imports
import asyncio
from pathlib import Path

# Third Party Imports
import ujson as json
import yaml
from aiofile import AIOFile
from pydantic import ValidationError

# Project Imports
from hyperglass.configuration.markdown import get_markdown
from hyperglass.configuration.models import commands as _commands
from hyperglass.configuration.models import params as _params
from hyperglass.configuration.models import routers as _routers
from hyperglass.constants import CREDIT
from hyperglass.constants import DEFAULT_HELP
from hyperglass.constants import DEFAULT_DETAILS
from hyperglass.constants import DEFAULT_TERMS
from hyperglass.constants import LOG_HANDLER
from hyperglass.constants import LOG_HANDLER_FILE
from hyperglass.constants import LOG_LEVELS
from hyperglass.constants import Supported
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
    try:
        params.branding.text.subtitle = params.branding.text.subtitle.format(
            **params.general.dict()
        )
    except KeyError:
        pass

    if user_commands:
        commands = _commands.Commands.import_params(user_commands)
    elif not user_commands:
        commands = _commands.Commands()

    devices = _routers.Routers._import(user_devices.get("routers", {}))

except ValidationError as validation_errors:
    errors = validation_errors.errors()
    log.error(errors)
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
                    "vrfs": [
                        {"id": vrf.name, "display_name": vrf.display_name}
                        for vrf in device.vrfs
                    ],
                }
            )
        elif device.name not in frontend_dict:
            frontend_dict[device.name] = {
                "location": device.location,
                "network": device.network.display_name,
                "display_name": device.display_name,
                "vrfs": [
                    {"id": vrf.name, "display_name": vrf.display_name}
                    for vrf in device.vrfs
                ],
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
    networks = []
    _networks = list(set({device.network.display_name for device in devices.routers}))

    for _network in _networks:
        network_def = {"display_name": _network, "locations": []}
        for device in devices.routers:
            if device.network.display_name == _network:
                network_def["locations"].append(
                    {
                        "name": device.name,
                        "location": device.location,
                        "display_name": device.display_name,
                        "network": device.network.display_name,
                        "vrfs": [
                            {"id": vrf.name, "display_name": vrf.display_name}
                            for vrf in device.vrfs
                        ],
                    }
                )
        networks.append(network_def)

    if not networks:
        raise ConfigError(error_msg="Unable to build network to device mapping")
    return networks


def _build_vrfs():
    vrfs = []
    for device in devices.routers:
        for vrf in device.vrfs:
            vrf_dict = {"id": vrf.name, "display_name": vrf.display_name}
            if vrf_dict not in vrfs:
                vrfs.append(vrf_dict)
    return vrfs


def _build_queries():
    """Build a dict of supported query types and their display names.

    Returns:
        {dict} -- Supported query dict
    """
    queries = []
    for query in Supported.query_types:
        display_name = getattr(params.branding.text, query)
        queries.append({"name": query, "display_name": display_name})
    return queries


content_params = json.loads(
    params.general.json(
        include={"primary_asn", "org_name", "site_title", "site_description"}
    )
)


def _build_vrf_help():
    """Build a dict of vrfs as keys, help content as values.

    Returns:
        {dict} -- Formatted VRF help
    """
    all_help = {}
    for vrf in devices.vrf_objects:
        vrf_help = {}
        for command in Supported.query_types:
            cmd = getattr(vrf.info, command)
            help_params = content_params
            if cmd.params.title is None:
                cmd.params.title = (
                    f"{vrf.display_name}: {getattr(params.branding.text, command)}"
                )
            help_params.update(cmd.params.dict())
            md = asyncio.run(
                get_markdown(
                    config_path=cmd,
                    default=DEFAULT_DETAILS[command],
                    params=help_params,
                )
            )
            vrf_help.update(
                {command: {"content": md, "enable": cmd.enable, "params": help_params}}
            )
        all_help.update({vrf.name: vrf_help})
    return all_help


content_vrf = _build_vrf_help()

content_help = asyncio.run(
    get_markdown(
        config_path=params.branding.help_menu,
        default=DEFAULT_HELP,
        params=content_params,
    )
)
content_terms = asyncio.run(
    get_markdown(
        config_path=params.branding.terms, default=DEFAULT_TERMS, params=content_params
    )
)
content_credit = CREDIT

vrfs = _build_vrfs()
queries = _build_queries()
networks = _build_networks()
frontend_networks = _build_frontend_networks()
frontend_devices = _build_frontend_devices()
_frontend_fields = {
    "general": {
        "debug",
        "primary_asn",
        "request_timeout",
        "org_name",
        "google_analytics",
        "opengraph",
        "site_descriptin",
    },
    "branding": ...,
    "features": {
        "bgp_route": {"enable"},
        "bgp_community": {"enable"},
        "bgp_aspath": {"enable"},
        "ping": {"enable"},
        "traceroute": {"enable"},
    },
    "messages": ...,
}
_frontend_params = params.dict(include=_frontend_fields)
_frontend_params.update(
    {
        "queries": queries,
        "devices": frontend_devices,
        "networks": networks,
        "vrfs": vrfs,
        "content": {
            "help_menu": content_help,
            "terms": content_terms,
            "credit": content_credit,
            "vrf": content_vrf,
        },
    }
)
frontend_params = _frontend_params
