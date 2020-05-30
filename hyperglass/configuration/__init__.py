"""Import configuration files and returns default values if undefined."""

# Standard Library
import os
import copy
import json
from pathlib import Path

# Third Party
import yaml
from pydantic import ValidationError

# Project
from hyperglass.log import (
    log,
    set_log_level,
    enable_file_logging,
    enable_syslog_logging,
)
from hyperglass.util import check_path, set_app_path, set_cache_env
from hyperglass.constants import (
    CREDIT,
    DEFAULT_HELP,
    DEFAULT_TERMS,
    TRANSPORT_REST,
    DEFAULT_DETAILS,
    SUPPORTED_QUERY_TYPES,
    PARSED_RESPONSE_FIELDS,
    SUPPORTED_STRUCTURED_OUTPUT,
    __version__,
)
from hyperglass.exceptions import ConfigError, ConfigInvalid, ConfigMissing
from hyperglass.configuration.models import params as _params
from hyperglass.configuration.models import routers as _routers
from hyperglass.configuration.models import commands as _commands
from hyperglass.configuration.markdown import get_markdown

set_app_path(required=True)

CONFIG_PATH = Path(os.environ["hyperglass_directory"])
log.info("Configuration directory: {d}", d=str(CONFIG_PATH))

# Project Directories
WORKING_DIR = Path(__file__).resolve().parent
CONFIG_FILES = (
    ("hyperglass.yaml", False),
    ("devices.yaml", True),
    ("commands.yaml", False),
)


def _check_config_files(directory):
    """Verify config files exist and are readable.

    Arguments:
        directory {Path} -- Config directory Path object

    Raises:
        ConfigMissing: Raised if a required config file does not pass checks.

    Returns:
        {tuple} -- main config, devices config, commands config
    """
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
        files += (file_path,)

    return files


STATIC_PATH = CONFIG_PATH / "static"

CONFIG_MAIN, CONFIG_DEVICES, CONFIG_COMMANDS = _check_config_files(CONFIG_PATH)


def _config_required(config_path: Path) -> dict:
    try:
        with config_path.open("r") as cf:
            config = yaml.safe_load(cf)
            log.debug(
                "Unvalidated data from file '{f}': {c}", f=str(config_path), c=config
            )
    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(str(yaml_error))
    return config


def _config_optional(config_path: Path) -> dict:
    if config_path is None:
        config = {}
    else:
        try:
            with config_path.open("r") as cf:
                config = yaml.safe_load(cf) or {}
                log.debug(
                    "Unvalidated data from file '{f}': {c}",
                    f=str(config_path),
                    c=config,
                )
        except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
            raise ConfigError(error_msg=str(yaml_error))
    return config


def _validate_nos_commands(all_nos, commands):
    nos_with_commands = commands.dict().keys()

    for nos in all_nos:
        valid = False
        if nos in SUPPORTED_STRUCTURED_OUTPUT:
            valid = True
        elif nos in TRANSPORT_REST:
            valid = True
        elif nos in nos_with_commands:
            valid = True

        if not valid:
            raise ConfigError(
                '"{nos}" is used on a device, '
                + 'but no command profile for "{nos}" is defined.',
                nos=nos,
            )

    return True


user_config = _config_optional(CONFIG_MAIN)

# Read raw debug value from config to enable debugging quickly.
set_log_level(logger=log, debug=user_config.get("debug", True))

_user_commands = _config_optional(CONFIG_COMMANDS)
_user_devices = _config_required(CONFIG_DEVICES)

# Map imported user config files to expected schema:
try:
    params = _params.Params(**user_config)
    commands = _commands.Commands.import_params(_user_commands)
    devices = _routers.Routers._import(_user_devices.get("routers", {}))
except ValidationError as validation_errors:
    errors = validation_errors.errors()
    log.error(errors)
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

_validate_nos_commands(devices.all_nos, commands)

set_cache_env(db=params.cache.database, host=params.cache.host, port=params.cache.port)

# Re-evaluate debug state after config is validated
set_log_level(logger=log, debug=params.debug)

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
        logger=log,
        syslog_host=params.logging.syslog.host,
        syslog_port=params.logging.syslog.port,
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
    if _params.Params().site_keywords == params.site_keywords:
        params.site_keywords = sorted(
            {*params.site_keywords, params.org_name, params.site_title}
        )

except KeyError:
    pass


def _build_frontend_networks():
    """Build filtered JSON structure of networks for frontend.

    Schema:
    {
        "device.network.display_name": {
            "device.name": {
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
                        "display_name": device.network.display_name,
                        "vrfs": [vrf.display_name for vrf in device.vrfs],
                    }
                }
            )
        elif device.network.display_name not in frontend_dict:
            frontend_dict[device.network.display_name] = {
                device.name: {
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
                    "network": device.network.display_name,
                    "display_name": device.display_name,
                    "vrfs": [
                        {
                            "id": vrf.name,
                            "display_name": vrf.display_name,
                            "ipv4": True if vrf.ipv4 else False,  # noqa: IF100
                            "ipv6": True if vrf.ipv6 else False,  # noqa: IF100
                        }
                        for vrf in device.vrfs
                    ],
                }
            )
        elif device.name not in frontend_dict:
            frontend_dict[device.name] = {
                "network": device.network.display_name,
                "display_name": device.display_name,
                "vrfs": [
                    {
                        "id": vrf.name,
                        "display_name": vrf.display_name,
                        "ipv4": True if vrf.ipv4 else False,  # noqa: IF100
                        "ipv6": True if vrf.ipv6 else False,  # noqa: IF100
                    }
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

            vrf_dict = {
                "id": vrf.name,
                "display_name": vrf.display_name,
            }

            if vrf_dict not in vrfs:
                vrfs.append(vrf_dict)

    return vrfs


content_params = json.loads(
    params.json(include={"primary_asn", "org_name", "site_title", "site_description"})
)


def _build_vrf_help():
    """Build a dict of vrfs as keys, help content as values.

    Returns:
        {dict} -- Formatted VRF help
    """
    all_help = {}
    for vrf in devices.vrf_objects:

        vrf_help = {}
        for command in SUPPORTED_QUERY_TYPES:
            cmd = getattr(vrf.info, command)
            if cmd.enable:
                help_params = {**content_params, **cmd.params.dict()}

                if help_params["title"] is None:
                    command_params = getattr(params.queries, command)
                    help_params[
                        "title"
                    ] = f"{vrf.display_name}: {command_params.display_name}"

                md = get_markdown(
                    config_path=cmd,
                    default=DEFAULT_DETAILS[command],
                    params=help_params,
                )

                vrf_help.update(
                    {
                        command: {
                            "content": md,
                            "enable": cmd.enable,
                            "params": help_params,
                        }
                    }
                )

        all_help.update({vrf.name: vrf_help})

    return all_help


content_greeting = get_markdown(
    config_path=params.web.greeting,
    default="",
    params={"title": params.web.greeting.title},
)

content_vrf = _build_vrf_help()

content_help_params = copy.copy(content_params)
content_help_params["title"] = params.web.help_menu.title
content_help = get_markdown(
    config_path=params.web.help_menu, default=DEFAULT_HELP, params=content_help_params
)

content_terms_params = copy.copy(content_params)
content_terms_params["title"] = params.web.terms.title
content_terms = get_markdown(
    config_path=params.web.terms, default=DEFAULT_TERMS, params=content_terms_params
)
content_credit = CREDIT.format(version=__version__)

vrfs = _build_vrfs()
networks = _build_networks()
frontend_networks = _build_frontend_networks()
frontend_devices = _build_frontend_devices()
_frontend_fields = {
    "cache": {"show_text", "timeout"},
    "debug": ...,
    "developer_mode": ...,
    "primary_asn": ...,
    "request_timeout": ...,
    "org_name": ...,
    "google_analytics": ...,
    "site_description": ...,
    "site_keywords": ...,
    "web": ...,
    "messages": ...,
}
_frontend_params = params.dict(include=_frontend_fields)
_frontend_params.update(
    {
        "hyperglass_version": __version__,
        "queries": {**params.queries.map, "list": params.queries.list},
        "devices": frontend_devices,
        "networks": networks,
        "vrfs": vrfs,
        "parsed_data_fields": PARSED_RESPONSE_FIELDS,
        "content": {
            "help_menu": content_help,
            "terms": content_terms,
            "credit": content_credit,
            "vrf": content_vrf,
            "greeting": content_greeting,
        },
    }
)
frontend_params = _frontend_params

URL_DEV = f"http://localhost:{str(params.listen_port)}/"
URL_PROD = "/api/"

REDIS_CONFIG = {
    "host": str(params.cache.host),
    "port": params.cache.port,
    "decode_responses": True,
}
