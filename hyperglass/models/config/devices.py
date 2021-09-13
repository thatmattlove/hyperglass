"""Validate router configuration variables."""

# Standard Library
import os
import re
from typing import Any, Set, Dict, List, Tuple, Union, Optional
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, validator, root_validator

# Project
from hyperglass.log import log
from hyperglass.util import get_driver, get_fmt_keys, validate_nos, resolve_hostname
from hyperglass.constants import SCRAPE_HELPERS, SUPPORTED_STRUCTURED_OUTPUT
from hyperglass.exceptions.private import ConfigError, UnsupportedDevice
from hyperglass.models.commands.generic import Directive

# Local
from .ssl import Ssl
from ..main import HyperglassModel, HyperglassModelWithId
from .proxy import Proxy
from .params import Params
from ..fields import SupportedDriver
from .network import Network
from .credential import Credential


class Device(HyperglassModelWithId, extra="allow"):
    """Validation model for per-router config in devices.yaml."""

    id: StrictStr
    name: StrictStr
    address: Union[IPv4Address, IPv6Address, StrictStr]
    network: Network
    credential: Credential
    proxy: Optional[Proxy]
    display_name: Optional[StrictStr]
    port: StrictInt = 22
    ssl: Optional[Ssl]
    nos: StrictStr
    commands: List[Directive]
    structured_output: Optional[StrictBool]
    driver: Optional[SupportedDriver]
    attrs: Dict[str, str] = {}

    def __init__(self, **kwargs) -> None:
        """Set the device ID."""
        _id, values = self._generate_id(kwargs)
        super().__init__(id=_id, **values)
        self._validate_directive_attrs()

    @property
    def _target(self):
        return str(self.address)

    @staticmethod
    def _generate_id(values: Dict) -> Tuple[str, Dict]:
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

        return device_id, {"name": display_name, "display_name": None, **values}

    def export_api(self) -> Dict[str, Any]:
        """Export API-facing device fields."""
        return {
            "id": self.id,
            "name": self.name,
            "network": self.network.display_name,
        }

    @property
    def directive_commands(self) -> List[str]:
        """Get all commands associated with the device."""
        return [
            command
            for directive in self.commands
            for rule in directive.rules
            for command in rule.commands
        ]

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

    @validator("structured_output", pre=True, always=True)
    def validate_structured_output(cls, value: bool, values: Dict) -> bool:
        """Validate structured output is supported on the device & set a default."""

        if value is True and values["nos"] not in SUPPORTED_STRUCTURED_OUTPUT:
            raise ConfigError(
                "The 'structured_output' field is set to 'true' on device '{d}' with "
                + "NOS '{n}', which does not support structured output",
                d=values["name"],
                n=values["nos"],
            )

        elif value is None and values["nos"] in SUPPORTED_STRUCTURED_OUTPUT:
            value = True
        else:
            value = False

        return value

    @validator("ssl")
    def validate_ssl(cls, value, values):
        """Set default cert file location if undefined."""

        if value is not None:
            if value.enable and value.cert is None:
                app_path = Path(os.environ["hyperglass_directory"])
                cert_file = app_path / "certs" / f'{values["name"]}.pem'
                if not cert_file.exists():
                    log.warning("No certificate found for device {d}", d=values["name"])
                    cert_file.touch()
                value.cert = cert_file
        return value

    @root_validator(pre=True)
    def validate_nos_commands(cls, values: Dict) -> Dict:
        """Validate & rewrite NOS, set default commands."""

        nos = values.get("nos", "")
        if not nos:
            # Ensure nos is defined.
            raise ValueError(
                f"Device {values['name']} is missing a 'nos' (Network Operating System) property."
            )

        if nos in SCRAPE_HELPERS.keys():
            # Rewrite NOS to helper value if needed.
            nos = SCRAPE_HELPERS[nos]

        # Verify NOS is supported by hyperglass.
        supported, _ = validate_nos(nos)
        if not supported:
            raise UnsupportedDevice(nos=nos)

        values["nos"] = nos

        commands = values.get("commands")

        if commands is None:
            # If no commands are defined, set commands to the NOS.
            inferred = values["nos"]

            # If the _telnet prefix is added, remove it from the command
            # profile so the commands are the same regardless of
            # protocol.
            if "_telnet" in inferred:
                inferred = inferred.replace("_telnet", "")

            values["commands"] = [inferred]

        return values

    @validator("driver")
    def validate_driver(cls, value: Optional[str], values: Dict) -> Dict:
        """Set the correct driver and override if supported."""
        return get_driver(values["nos"], value)


class Devices(HyperglassModel, extra="allow"):
    """Validation model for device configurations."""

    ids: List[StrictStr] = []
    hostnames: List[StrictStr] = []
    objects: List[Device] = []
    all_nos: List[StrictStr] = []

    def __init__(self, input_params: List[Dict]) -> None:
        """Import loaded YAML, initialize per-network definitions.

        Remove unsupported characters from device names, dynamically
        set attributes for the devices class. Builds lists of common
        attributes for easy access in other modules.
        """
        all_nos = set()
        objects = set()
        hostnames = set()
        ids = set()

        init_kwargs = {}

        for definition in input_params:
            # Validate each router config against Router() model/schema
            device = Device(**definition)

            # Add router-level attributes (assumed to be unique) to
            # class lists, e.g. so all hostnames can be accessed as a
            # list with `devices.hostnames`, same for all router
            # classes, for when iteration over all routers is required.
            hostnames.add(device.name)
            ids.add(device.id)
            objects.add(device)
            all_nos.add(device.nos)

        # Convert the de-duplicated sets to a standard list, add lists
        # as class attributes. Sort router list by router name attribute
        init_kwargs["ids"] = list(ids)
        init_kwargs["hostnames"] = list(hostnames)
        init_kwargs["all_nos"] = list(all_nos)
        init_kwargs["objects"] = sorted(objects, key=lambda x: x.name)

        super().__init__(**init_kwargs)

    def __getitem__(self, accessor: str) -> Device:
        """Get a device by its name."""
        for device in self.objects:
            if device.id == accessor:
                return device
            elif device.name == accessor:
                return device

        raise AttributeError(f"No device named '{accessor}'")

    def export_api(self) -> List[Dict[str, Any]]:
        """Export API-facing device fields."""
        return [d.export_api() for d in self.objects]

    def networks(self, params: Params) -> List[Dict[str, Any]]:
        """Group devices by network."""
        names = {device.network.display_name for device in self.objects}
        return [
            {
                "display_name": name,
                "locations": [
                    {
                        "id": device.id,
                        "name": device.name,
                        "network": device.network.display_name,
                        "directives": [c.frontend(params) for c in device.commands],
                    }
                    for device in self.objects
                    if device.network.display_name == name
                ],
            }
            for name in names
        ]

    def directive_plugins(self) -> Dict[Path, Tuple[StrictStr]]:
        """Get a mapping of plugin paths to associated directive IDs."""
        result: Dict[Path, Set[StrictStr]] = {}
        # Unique set of all directives.
        directives = {directive for device in self.objects for directive in device.commands}
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
