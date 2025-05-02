"""Import configuration files and run validation."""

# Third Party
from pydantic import ValidationError

# Project
from hyperglass.log import log
from hyperglass.settings import Settings
from hyperglass.models.ui import UIParameters
from hyperglass.models.directive import Directive, Directives
from hyperglass.exceptions.private import ConfigError, ConfigInvalid
from hyperglass.models.config.params import Params
from hyperglass.models.config.devices import Devices

# Local
from .load import load_config
from .markdown import get_markdown

__all__ = (
    "init_devices",
    "init_directives",
    "init_files",
    "init_params",
    "init_ui_params",
)


def init_files() -> None:
    """Check if required directories exist and if not, create them."""
    for directory in ("plugins", "static/images"):
        path = Settings.app_path / directory
        if not path.exists():
            path.mkdir(parents=True)
            log.debug("Created directory", path=path)


def init_params() -> "Params":
    """Validate & initialize configuration parameters."""
    user_config = load_config("config", required=False)
    # Map imported user configuration to expected schema.
    params = Params(**user_config)

    # # Set up file logging once configuration parameters are initialized.
    # enable_file_logging(
    #     log_directory=params.logging.directory,
    #     log_format=params.logging.format,
    #     log_max_size=params.logging.max_size,
    #     debug=Settings.debug,
    # )

    # Set up syslog logging if enabled.
    # if params.logging.syslog is not None and params.logging.syslog.enable:
    #     enable_syslog_logging(
    #         syslog_host=params.logging.syslog.host,
    #         syslog_port=params.logging.syslog.port,
    #     )

    if params.logging.http is not None and params.logging.http.enable:
        log.debug("HTTP logging is enabled")

    # Perform post-config initialization string formatting or other
    # functions that require access to other config levels. E.g.,
    # something in 'params.web.text' needs to be formatted with a value
    # from params.
    try:
        params.web.text.subtitle = params.web.text.subtitle.format(
            **params.model_dump(exclude={"web", "queries", "messages"})
        )
    except KeyError:
        pass

    return params


def init_directives() -> "Directives":
    """Validate & initialize directives."""
    # Map imported user directives to expected schema.
    directives = load_config("directives", required=False)
    try:
        directives = (
            Directive(id=name, **directive)
            for name, directive in load_config("directives", required=False).items()
        )

    except ValidationError as err:
        raise ConfigInvalid(errors=err.errors()) from err

    return Directives(*directives)


def init_devices() -> "Devices":
    """Validate & initialize devices."""
    devices_config = load_config("devices", required=True)
    items = []

    # Support first matching main key name.
    for key in ("main", "devices", "routers"):
        if key in devices_config:
            items = devices_config[key]
            break

    if len(items) < 1:
        raise ConfigError("No devices are defined in devices file")

    devices = Devices(*items)
    log.debug("Initialized devices", devices=devices)

    return devices


def init_ui_params(*, params: "Params", devices: "Devices") -> "UIParameters":
    """Validate & initialize UI parameters."""

    # Project
    from hyperglass.defaults import CREDIT
    from hyperglass.constants import PARSED_RESPONSE_FIELDS, __version__

    content_greeting = get_markdown(
        config=params.web.greeting,
        default="",
        params={"title": params.web.greeting.title},
    )
    content_credit = CREDIT.format(version=__version__)

    _ui_params = params.frontend()
    _ui_params["web"]["logo"]["light_format"] = params.web.logo.light.suffix
    _ui_params["web"]["logo"]["dark_format"] = params.web.logo.dark.suffix

    return UIParameters(
        **_ui_params,
        version=__version__,
        devices=devices.frontend(),
        developer_mode=Settings.dev_mode,
        parsed_data_fields=PARSED_RESPONSE_FIELDS,
        content={"credit": content_credit, "greeting": content_greeting},
    )
