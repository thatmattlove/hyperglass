"""Validate router configuration variables."""

# Standard Library
import os
import re
from typing import Any, Dict, List, Union, Optional
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, validator

# Project
from hyperglass.log import log
from hyperglass.util import validate_nos, resolve_hostname
from hyperglass.models import HyperglassModel, HyperglassModelExtra
from hyperglass.constants import SCRAPE_HELPERS, SUPPORTED_STRUCTURED_OUTPUT
from hyperglass.exceptions import ConfigError, UnsupportedDevice
from hyperglass.configuration.models.ssl import Ssl
from hyperglass.configuration.models.vrf import Vrf, Info
from hyperglass.configuration.models.proxy import Proxy
from hyperglass.configuration.models.network import Network
from hyperglass.configuration.models.credential import Credential

_default_vrf = {
    "name": "default",
    "display_name": "Global",
    "info": Info(),
    "ipv4": {
        "source_address": None,
        "access_list": [
            {"network": "0.0.0.0/0", "action": "permit", "ge": 0, "le": 32}
        ],
    },
    "ipv6": {
        "source_address": None,
        "access_list": [{"network": "::/0", "action": "permit", "ge": 0, "le": 128}],
    },
}


class Device(HyperglassModel):
    """Validation model for per-router config in devices.yaml."""

    name: StrictStr
    address: Union[IPv4Address, IPv6Address, StrictStr]
    network: Network
    credential: Credential
    proxy: Optional[Proxy]
    display_name: StrictStr
    port: StrictInt
    ssl: Optional[Ssl]
    nos: StrictStr
    commands: Optional[StrictStr]
    vrfs: List[Vrf] = [_default_vrf]
    display_vrfs: List[StrictStr] = []
    vrf_names: List[StrictStr] = []
    structured_output: Optional[StrictBool]

    def __hash__(self) -> int:
        """Make device object hashable so the object can be deduplicated with set()."""
        return hash((self.name,))

    def __eq__(self, other: Any) -> bool:
        """Make device object comparable so the object can be deduplicated with set()."""
        result = False

        if isinstance(other, HyperglassModel):
            result = self.name == other.name

        return result

    @property
    def _target(self):
        return str(self.address)

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
    def validate_structured_output(cls, value, values):
        """Validate structured output is supported on the device & set a default.

        Raises:
            ConfigError: Raised if true on a device that doesn't support structured output.

        Returns:
            {bool} -- True if hyperglass should return structured output for this device.
        """
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

    @validator("nos")
    def supported_nos(cls, value):
        """Validate that nos is supported by hyperglass.

        Raises:
            UnsupportedDevice: Raised if nos is unsupported.

        Returns:
            {str} -- Valid NOS
        """
        if value in SCRAPE_HELPERS.keys():
            value = SCRAPE_HELPERS[value]

        supported, _ = validate_nos(value)

        if not supported:
            raise UnsupportedDevice('"{nos}" is not supported.', nos=value)

        return value

    @validator("ssl")
    def validate_ssl(cls, value, values):
        """Set default cert file location if undefined.

        Arguments:
            value {object} -- SSL object
            values {dict} -- Other already-validated fields

        Returns:
            {object} -- SSL configuration
        """
        if value is not None:
            if value.enable and value.cert is None:
                app_path = Path(os.environ["hyperglass_directory"])
                cert_file = app_path / "certs" / f'{values["name"]}.pem'
                if not cert_file.exists():
                    log.warning("No certificate found for device {d}", d=values["name"])
                    cert_file.touch()
                value.cert = cert_file
        return value

    @validator("commands", always=True)
    def validate_commands(cls, value, values):
        """If a named command profile is not defined, use the NOS name.

        Arguments:
            value {str} -- Reference to command profile
            values {dict} -- Other already-validated fields

        Returns:
            {str} -- Command profile or NOS name
        """
        if value is None:
            value = values["nos"]
        return value

    @validator("vrfs", pre=True)
    def validate_vrfs(cls, value, values):
        """Validate VRF definitions.

          - Ensures source IP addresses are set for the default VRF
            (global routing table).
          - Initializes the default VRF with the DefaultVRF() class so
            that specific defaults can be set for the global routing
            table.
          - If the 'display_name' is not set for a non-default VRF, try
            to make one that looks pretty based on the 'name'.

        Arguments:
            value {list} -- List of VRFs
            values {dict} -- Other already-validated fields

        Raises:
            ConfigError: Raised if the VRF is missing a source address

        Returns:
            {list} -- List of valid VRFs
        """
        vrfs = []
        for vrf in value:
            vrf_name = vrf.get("name")

            for afi in ("ipv4", "ipv6"):
                vrf_afi = vrf.get(afi)

                # If AFI is actually defined (enabled), and if the
                # source_address field is not set, raise an error
                if vrf_afi is not None and vrf_afi.get("source_address") is None:
                    raise ConfigError(
                        (
                            "VRF '{vrf}' in router '{router}' is missing a source "
                            "{afi} address."
                        ),
                        vrf=vrf.get("name"),
                        router=values.get("name"),
                        afi=afi.replace("ip", "IP"),
                    )

            # If no display_name is set for a non-default VRF, try
            # to make one by replacing non-alphanumeric characters
            # with whitespaces and using str.title() to make each
            # word look "pretty".
            if vrf_name != "default" and not isinstance(
                vrf.get("display_name"), StrictStr
            ):
                new_name = vrf["name"]
                new_name = re.sub(r"[^a-zA-Z0-9]", " ", new_name)
                new_name = re.split(" ", new_name)
                vrf["display_name"] = " ".join([w.title() for w in new_name])

                log.debug(
                    f'Field "display_name" for VRF "{vrf["name"]}" was not set. '
                    f"Generated '{vrf['display_name']}'"
                )

            elif vrf_name == "default" and vrf.get("display_name") is None:
                vrf["display_name"] = "Global"

            # Validate the non-default VRF against the standard
            # Vrf() class.
            vrf = Vrf(**vrf)

            vrfs.append(vrf)
        return vrfs


class Devices(HyperglassModelExtra):
    """Validation model for device configurations."""

    hostnames: List[StrictStr] = []
    vrfs: List[StrictStr] = []
    display_vrfs: List[StrictStr] = []
    vrf_objects: List[Vrf] = []
    objects: List[Device] = []
    all_nos: List[StrictStr] = []
    default_vrf: Vrf = Vrf(name="default", display_name="Global")

    def __init__(self, input_params: List[Dict]) -> None:
        """Import loaded YAML, initialize per-network definitions.

        Remove unsupported characters from device names, dynamically
        set attributes for the devices class. Builds lists of common
        attributes for easy access in other modules.

        Arguments:
            input_params {dict} -- Unvalidated router definitions

        Returns:
            {object} -- Validated routers object
        """
        vrfs = set()
        display_vrfs = set()
        vrf_objects = set()
        all_nos = set()
        objects = set()
        hostnames = set()

        init_kwargs = {}

        for definition in input_params:
            # Validate each router config against Router() model/schema
            device = Device(**definition)

            # Add router-level attributes (assumed to be unique) to
            # class lists, e.g. so all hostnames can be accessed as a
            # list with `devices.hostnames`, same for all router
            # classes, for when iteration over all routers is required.
            hostnames.add(device.name)
            objects.add(device)
            all_nos.add(device.nos)

            for vrf in device.vrfs:

                # For each configured router VRF, add its name and
                # display_name to a class set (for automatic de-duping).
                vrfs.add(vrf.name)
                display_vrfs.add(vrf.display_name)

                # Also add the names to a router-level list so each
                # router's VRFs and display VRFs can be easily accessed.
                device.display_vrfs.append(vrf.display_name)
                device.vrf_names.append(vrf.name)

                # Add a 'default_vrf' attribute to the devices class
                # which contains the configured default VRF display name.
                if vrf.name == "default" and not hasattr(self, "default_vrf"):
                    init_kwargs["default_vrf"] = Vrf(
                        name=vrf.name, display_name=vrf.display_name
                    )

                # Add the native VRF objects to a set (for automatic
                # de-duping), but exlcude device-specific fields.
                vrf_objects.add(
                    vrf.copy(
                        deep=True,
                        exclude={
                            "ipv4": {"source_address"},
                            "ipv6": {"source_address"},
                        },
                    )
                )

        # Convert the de-duplicated sets to a standard list, add lists
        # as class attributes. Sort router list by router name attribute
        init_kwargs["hostnames"] = list(hostnames)
        init_kwargs["all_nos"] = list(all_nos)
        init_kwargs["vrfs"] = list(vrfs)
        init_kwargs["display_vrfs"] = list(vrfs)
        init_kwargs["vrf_objects"] = list(vrf_objects)
        init_kwargs["objects"] = sorted(objects, key=lambda x: x.display_name)

        super().__init__(**init_kwargs)

    def __getitem__(self, accessor: str) -> Device:
        """Get a device by its name."""
        for device in self.objects:
            if device.name == accessor:
                return device

        raise AttributeError(f"No device named '{accessor}'")
