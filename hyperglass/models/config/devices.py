"""Validate router configuration variables."""

# Standard Library
import re
from typing import Any, Set, Dict, List, Tuple, Union, Optional
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address

# Third Party
from pydantic import FilePath, StrictInt, StrictStr, StrictBool, validator
from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

# Project
from hyperglass.log import log
from hyperglass.util import get_driver, get_fmt_keys, resolve_hostname
from hyperglass.state import use_state
from hyperglass.settings import Settings
from hyperglass.constants import DRIVER_MAP, SCRAPE_HELPERS, SUPPORTED_STRUCTURED_OUTPUT
from hyperglass.exceptions.private import ConfigError, UnsupportedDevice

# Local
from .ssl import Ssl
from ..main import MultiModel, HyperglassModel, HyperglassModelWithId
from ..util import check_legacy_fields
from .proxy import Proxy
from ..fields import SupportedDriver
from ..directive import Directives
from .credential import Credential

ALL_DEVICE_TYPES = {*DRIVER_MAP.keys(), *CLASS_MAPPER.keys()}


class DirectiveOptions(HyperglassModel, extra="ignore"):
    """Per-device directive options."""

    builtins: Union[StrictBool, List[StrictStr]] = True


class Device(HyperglassModelWithId, extra="allow"):
    """Validation model for per-router config in devices.yaml."""

    id: StrictStr
    name: StrictStr
    description: Optional[StrictStr]
    avatar: Optional[FilePath]
    address: Union[IPv4Address, IPv6Address, StrictStr]
    group: Optional[StrictStr]
    credential: Credential
    proxy: Optional[Proxy]
    display_name: Optional[StrictStr]
    port: StrictInt = 22
    ssl: Optional[Ssl]
    platform: StrictStr
    structured_output: Optional[StrictBool]
    directives: Directives = Directives()
    driver: Optional[SupportedDriver]
    attrs: Dict[str, str] = {}

    def __init__(self, **kw) -> None:
        """Check legacy fields and ensure an `id` is set."""
        kw = check_legacy_fields(model="Device", data=kw)
        if "id" not in kw:
            kw = self._with_id(kw)
        super().__init__(**kw)
        self._validate_directive_attrs()

    @property
    def _target(self):
        return str(self.address)

    @staticmethod
    def _with_id(values: Dict) -> str:
        """Generate device id & handle legacy display_name field."""

        def generate_id(name: str) -> str:
            scrubbed = re.sub(r"[^A-Za-z0-9\_\-\s]", "", name)
            return "_".join(scrubbed.split()).lower()

        name = values.pop("name", None)

        if name is None:
            raise ValueError("name is required.")

        legacy_display_name = values.pop("display_name", None)

        if legacy_display_name is not None:
            log.warning("The 'display_name' field is deprecated. Use the 'name' field instead.")
            device_id = generate_id(legacy_display_name)
            display_name = legacy_display_name
        else:
            device_id = generate_id(name)
            display_name = name

        return {"id": device_id, "name": display_name, "display_name": None, **values}

    def export_api(self) -> Dict[str, Any]:
        """Export API-facing device fields."""
        return {
            "id": self.id,
            "name": self.name,
            "group": self.group,
        }

    @property
    def directive_commands(self) -> List[str]:
        """Get all commands associated with the device."""
        return [
            command
            for directive in self.directives
            for rule in directive.rules
            for command in rule.commands
        ]

    @property
    def directive_ids(self) -> List[str]:
        """Get all directive IDs associated with the device."""
        return [directive.id for directive in self.directives]

    def has_directives(self, *directive_ids: str) -> bool:
        """Determine if a directive is used on this device."""
        for directive_id in directive_ids:
            if directive_id in self.directive_ids:
                return True
        return False

    def _validate_directive_attrs(self) -> None:

        # Set of all keys except for built-in key `target`.
        keys = {
            key
            for group in [get_fmt_keys(command) for command in self.directive_commands]
            for key in group
            if key != "target"
        }

        attrs = {k: v for k, v in self.attrs.items() if k in keys}

        # Verify all keys in associated commands contain values in device's `attrs`.
        for key in keys:
            if key not in attrs:
                raise ConfigError(
                    "Device '{d}' has a command that references attribute '{a}', but '{a}' is missing from device attributes",
                    d=self.name,
                    a=key,
                )

    @validator("address")
    def validate_address(cls, value, values):
        """Ensure a hostname is resolvable."""

        if not isinstance(value, (IPv4Address, IPv6Address)):
            if not any(resolve_hostname(value)):
                raise ConfigError(
                    "Device '{d}' has an address of '{a}', which is not resolvable.",
                    d=values["name"],
                    a=value,
                )
        return value

    @validator("avatar")
    def validate_avatar(
        cls, value: Union[FilePath, None], values: Dict[str, Any]
    ) -> Union[FilePath, None]:
        """Migrate avatar to static directory."""
        if value is not None:
            # Standard Library
            import shutil

            # Third Party
            from PIL import Image

            target = Settings.static_path / "images" / value.name
            copied = shutil.copy2(value, target)
            log.debug("Copied {} avatar from {!r} to {!r}", values["name"], str(value), str(target))

            with Image.open(copied) as src:
                if src.width > 512:
                    src.thumbnail((512, 512 * src.height / src.width))
                    src.save(target)
        return value

    @validator("platform", pre=True, always=True)
    def validate_platform(cls: "Device", value: Any, values: Dict[str, Any]) -> str:
        """Validate & rewrite device platform, set default `directives`."""

        if value is None:
            # Ensure device platform is defined.
            raise ConfigError(
                "Device '{device}' is missing a 'platform' (Network Operating System) property",
                device=values["name"],
            )

        if value in SCRAPE_HELPERS.keys():
            # Rewrite platform to helper value if needed.
            value = SCRAPE_HELPERS[value]

        # Verify device platform is supported by hyperglass.
        if value not in ALL_DEVICE_TYPES:
            raise UnsupportedDevice(value)

        return value

    @validator("structured_output", pre=True, always=True)
    def validate_structured_output(cls, value: bool, values: Dict[str, Any]) -> bool:
        """Validate structured output is supported on the device & set a default."""

        if value is True:
            if values["platform"] not in SUPPORTED_STRUCTURED_OUTPUT:
                raise ConfigError(
                    "The 'structured_output' field is set to 'true' on device '{d}' with "
                    + "platform '{p}', which does not support structured output",
                    d=values["name"],
                    p=values["platform"],
                )
            return value
        elif value is None and values["platform"] in SUPPORTED_STRUCTURED_OUTPUT:
            value = True
        else:
            value = False
        return value

    @validator("ssl")
    def validate_ssl(cls, value, values):
        """Set default cert file location if undefined."""

        if value is not None:
            if value.enable and value.cert is None:
                cert_file = Settings.app_path / "certs" / f'{values["name"]}.pem'
                if not cert_file.exists():
                    log.warning("No certificate found for device {d}", d=values["name"])
                    cert_file.touch()
                value.cert = cert_file
        return value

    @validator("directives", pre=True, always=True)
    def validate_directives(cls: "Device", value, values) -> "Directives":
        """Associate directive IDs to loaded directive objects."""
        directives = use_state("directives")

        directive_ids = value or []
        structured_output = values.get("structured_output", False)
        platform = values.get("platform")

        # Directive options
        directive_options = DirectiveOptions(
            **{
                k: v
                for statement in directive_ids
                if isinstance(statement, Dict)
                for k, v in statement.items()
            }
        )

        # String directive IDs, excluding builtins and options.
        directive_ids = [
            statement
            for statement in directive_ids
            if isinstance(statement, str) and not statement.startswith("__")
        ]
        # Directives matching provided IDs.
        device_directives = directives.filter(*directive_ids)
        # Matching built-in directives for this device's platform.
        builtins = directives.device_builtins(platform=platform, table_output=structured_output)

        if directive_options.builtins is True:
            # Add all builtins.
            device_directives += builtins
        elif isinstance(directive_options.builtins, List):
            # If the user provides a list of builtin directives to include, add only those.
            device_directives += builtins.matching(*directive_options.builtins)

        return device_directives

    @validator("driver")
    def validate_driver(cls, value: Optional[str], values: Dict) -> Dict:
        """Set the correct driver and override if supported."""
        return get_driver(values["platform"], value)


class Devices(MultiModel, model=Device, unique_by="id"):
    """Container for all devices."""

    def __init__(self, *items: Dict[str, Any]) -> None:
        """Generate IDs prior to validation."""
        with_id = (Device._with_id(item) for item in items)
        super().__init__(*with_id)

    def export_api(self) -> List[Dict[str, Any]]:
        """Export API-facing device fields."""
        return [d.export_api() for d in self]

    def valid_id_or_name(self, value: str) -> bool:
        """Determine if a value is a valid device name or ID."""
        for device in self:
            if value == device.id or value == device.name:
                return True
        return False

    def directive_plugins(self) -> Dict[Path, Tuple[StrictStr]]:
        """Get a mapping of plugin paths to associated directive IDs."""
        result: Dict[Path, Set[StrictStr]] = {}
        # Unique set of all directives.
        directives = {directive for device in self for directive in device.directives}
        # Unique set of all plugin file names.
        plugin_names = {plugin for directive in directives for plugin in directive.plugins}

        for directive in directives:
            # Convert each plugin file name to a `Path` object.
            for plugin in (Path(p) for p in directive.plugins if p in plugin_names):
                if plugin not in result:
                    result[plugin] = set()
                result[plugin].add(directive.id)
        # Convert the directive set to a tuple.
        return {k: tuple(v) for k, v in result.items()}

    def frontend(self) -> List[Dict[str, Any]]:
        """Export grouped devices for UIParameters."""
        params = use_state("params")
        groups = {device.group for device in self}
        return [
            {
                "group": group,
                "locations": [
                    {
                        "group": group,
                        "id": device.id,
                        "name": device.name,
                        "avatar": f"/images/{device.avatar.name}"
                        if device.avatar is not None
                        else None,
                        "description": device.description,
                        "directives": [d.frontend(params) for d in device.directives],
                    }
                    for device in self
                    if device.group == group
                ],
            }
            for group in groups
        ]
