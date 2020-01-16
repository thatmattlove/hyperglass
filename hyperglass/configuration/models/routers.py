"""Validate router configuration variables."""

# Standard Library Imports
import re
from typing import List
from typing import Optional

# Third Party Imports
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import HyperglassModelExtra
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models.commands import Command
from hyperglass.configuration.models.credentials import Credential
from hyperglass.configuration.models.networks import Network
from hyperglass.configuration.models.proxies import Proxy
from hyperglass.configuration.models.ssl import Ssl
from hyperglass.configuration.models.vrfs import DefaultVrf
from hyperglass.configuration.models.vrfs import Vrf
from hyperglass.constants import Supported
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import UnsupportedDevice
from hyperglass.util import log


class Router(HyperglassModel):
    """Validation model for per-router config in devices.yaml."""

    name: StrictStr
    address: StrictStr
    network: Network
    credential: Credential
    proxy: Optional[Proxy]
    location: StrictStr
    display_name: StrictStr
    port: StrictInt
    ssl: Optional[Ssl]
    nos: StrictStr
    commands: Optional[Command]
    vrfs: List[Vrf] = [DefaultVrf()]
    display_vrfs: List[StrictStr] = []
    vrf_names: List[StrictStr] = []

    @validator("nos")
    def supported_nos(cls, value):
        """Validate that nos is supported by hyperglass.

        Raises:
            UnsupportedDevice: Raised if nos is unsupported.

        Returns:
            {str} -- Valid NOS
        """
        if not Supported.is_supported(value):
            raise UnsupportedDevice(f'"{value}" device type is not supported.')
        return value

    @validator("name", "location")
    def clean_name(cls, value):
        """Remove or replace unsupported characters from field values.

        Arguments:
            value {str} -- Raw name/location

        Returns:
            {} -- Valid name/location
        """
        return clean_name(value)

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

                if vrf_afi is not None and vrf_afi.get("source_address") is None:

                    # If AFI is actually defined (enabled), and if the
                    # source_address field is not set, raise an error
                    raise ConfigError(
                        (
                            "VRF '{vrf}' in router '{router}' is missing a source "
                            "{afi} address."
                        ),
                        vrf=vrf.get("name"),
                        router=values.get("name"),
                        afi=afi.replace("ip", "IP"),
                    )
            if vrf_name == "default":

                # Validate the default VRF against the DefaultVrf()
                # class. (See vrfs.py)
                vrf = DefaultVrf(**vrf)

            elif vrf_name != "default" and not isinstance(
                vrf.get("display_name"), StrictStr
            ):

                # If no display_name is set for a non-default VRF, try
                # to make one by replacing non-alphanumeric characters
                # with whitespaces and using str.title() to make each
                # word look "pretty".
                new_name = vrf["name"]
                new_name = re.sub(r"[^a-zA-Z0-9]", " ", new_name)
                new_name = re.split(" ", new_name)
                vrf["display_name"] = " ".join([w.title() for w in new_name])

                log.debug(
                    f'Field "display_name" for VRF "{vrf["name"]}" was not set. '
                    f"Generated '{vrf['display_name']}'"
                )

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
        routers = Routers()
        routers.routers = []
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
            routers.routers.append(router)

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
                # which contains the configured default VRF display name
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
        # as class attributes
        routers.vrfs = list(vrfs)
        routers.display_vrfs = list(display_vrfs)
        routers.vrf_objects = list(vrf_objects)
        routers.networks = list(networks)

        return routers
