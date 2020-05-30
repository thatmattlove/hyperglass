"""Validate router configuration variables."""

# Standard Library
import os
import re
from typing import List, Optional
from pathlib import Path

# Third Party
from pydantic import StrictInt, StrictStr, StrictBool, validator

# Project
from hyperglass.log import log
from hyperglass.util import clean_name, validate_nos
from hyperglass.models import HyperglassModel, HyperglassModelExtra
from hyperglass.constants import SCRAPE_HELPERS, SUPPORTED_STRUCTURED_OUTPUT
from hyperglass.exceptions import ConfigError, UnsupportedDevice
from hyperglass.configuration.models.ssl import Ssl
from hyperglass.configuration.models.vrfs import Vrf, Info
from hyperglass.configuration.models.proxies import Proxy
from hyperglass.configuration.models.networks import Network
from hyperglass.configuration.models.credentials import Credential
from hyperglass.configuration.models.commands.common import CommandGroup

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


class Router(HyperglassModel):
    """Validation model for per-router config in devices.yaml."""

    name: StrictStr
    address: StrictStr
    network: Network
    credential: Credential
    proxy: Optional[Proxy]
    display_name: StrictStr
    port: StrictInt
    ssl: Optional[Ssl]
    nos: StrictStr
    commands: Optional[CommandGroup]
    vrfs: List[Vrf] = [_default_vrf]
    display_vrfs: List[StrictStr] = []
    vrf_names: List[StrictStr] = []
    structured_output: Optional[StrictBool]

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

    @validator("name")
    def validate_name(cls, value):
        """Remove or replace unsupported characters from field values.

        Arguments:
            value {str} -- Raw name/location

        Returns:
            {} -- Valid name/location
        """
        return clean_name(value)

    @validator("ssl")
    def validate_ssl(cls, value, values):
        """Set default cert file location if undefined.

        Arguments:
            value {object} -- SSL object
            values {dict} -- Other already-valiated fields

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


class Routers(HyperglassModelExtra):
    """Validation model for device configurations."""

    hostnames: List[StrictStr] = []
    vrfs: List[StrictStr] = []
    display_vrfs: List[StrictStr] = []
    routers: List[Router] = []
    networks: List[StrictStr] = []

    @classmethod
    def _import(cls, input_params):
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
        networks = set()
        display_vrfs = set()
        vrf_objects = set()
        all_nos = set()
        router_objects = []
        routers = Routers()
        routers.hostnames = []
        routers.vrfs = []
        routers.display_vrfs = []

        for definition in input_params:
            # Validate each router config against Router() model/schema
            router = Router(**definition)

            # Set a class attribute for each router so each router's
            # attributes can be accessed with `devices.router_hostname`
            setattr(routers, router.name, router)

            # Add router-level attributes (assumed to be unique) to
            # class lists, e.g. so all hostnames can be accessed as a
            # list with `devices.hostnames`, same for all router
            # classes, for when iteration over all routers is required.
            routers.hostnames.append(router.name)
            router_objects.append(router)
            all_nos.add(router.nos)

            for vrf in router.vrfs:

                # For each configured router VRF, add its name and
                # display_name to a class set (for automatic de-duping).
                vrfs.add(vrf.name)
                display_vrfs.add(vrf.display_name)

                # Also add the names to a router-level list so each
                # router's VRFs and display VRFs can be easily accessed.
                router.display_vrfs.append(vrf.display_name)
                router.vrf_names.append(vrf.name)

                # Add a 'default_vrf' attribute to the devices class
                # which contains the configured default VRF display name.
                if vrf.name == "default" and not hasattr(cls, "default_vrf"):
                    routers.default_vrf = {
                        "name": vrf.name,
                        "display_name": vrf.display_name,
                    }

                # Add the native VRF objects to a set (for automatic
                # de-duping), but exlcude device-specific fields.
                _copy_params = {
                    "deep": True,
                    "exclude": {"ipv4": {"source_address"}, "ipv6": {"source_address"}},
                }
                vrf_objects.add(vrf.copy(**_copy_params))

        # Convert the de-duplicated sets to a standard list, add lists
        # as class attributes.
        routers.vrfs = list(vrfs)
        routers.display_vrfs = list(display_vrfs)
        routers.vrf_objects = list(vrf_objects)
        routers.networks = list(networks)
        routers.all_nos = list(all_nos)

        # Sort router list by router name attribute
        routers.routers = sorted(router_objects, key=lambda x: x.display_name)

        return routers
