"""Validate router configuration variables."""

# Standard Library Imports
import re
from typing import List
from typing import Union

# Third Party Imports
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import HyperglassModelExtra
from hyperglass.configuration.models._utils import clean_name
from hyperglass.configuration.models.commands import Command
from hyperglass.configuration.models.credentials import Credential
from hyperglass.configuration.models.networks import Network
from hyperglass.configuration.models.proxies import Proxy
from hyperglass.configuration.models.vrfs import DefaultVrf, Vrf
from hyperglass.constants import Supported
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import UnsupportedDevice
from hyperglass.util import log


class Router(HyperglassModel):
    """Validation model for per-router config in devices.yaml."""

    name: str
    address: str
    network: Network
    credential: Credential
    proxy: Union[Proxy, None] = None
    location: str
    display_name: str
    port: int
    nos: str
    commands: Union[Command, None] = None
    vrfs: List[Vrf] = [DefaultVrf()]
    display_vrfs: List[str] = []
    vrf_names: List[str] = []

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """
        Validates that passed nos string is supported by hyperglass.
        """
        if not Supported.is_supported(v):
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v

    @validator("name", "location")
    def clean_name(cls, v):  # noqa: N805
        """Remove or replace unsupported characters from field values"""
        return clean_name(v)

    @validator("commands", always=True)
    def validate_commands(cls, v, values):  # noqa: N805
        """
        If a named command profile is not defined, use the NOS name.
        """
        if v is None:
            v = values["nos"]
        return v

    @validator("vrfs", pre=True, whole=True)
    def validate_vrfs(cls, value, values):
        """
          - Ensures source IP addresses are set for the default VRF
            (global routing table).
          - Initializes the default VRF with the DefaultVRF() class so
            that specific defaults can be set for the global routing
            table.
          - If the 'display_name' is not set for a non-default VRF, try
            to make one that looks pretty based on the 'name'.
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

            elif vrf_name != "default" and not isinstance(vrf.get("display_name"), str):

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
                    f'Generated "display_name" {vrf["display_name"]}'
                )
                # Validate the non-default VRF against the standard
                # Vrf() class.
                vrf = Vrf(**vrf)

            vrfs.append(vrf)
        return vrfs


class Routers(HyperglassModelExtra):
    """Validation model for device configurations."""

    hostnames: List[str] = []
    vrfs: List[str] = []
    display_vrfs: List[str] = []
    routers: List[Router] = []

    @classmethod
    def _import(cls, input_params):
        """
        Imports passed list of dictionaries from YAML config, validates
        each router config, sets class attributes for each router for
        easy access. Also builds lists of common attributes for easy
        access in other modules.
        """
        vrfs = set()
        display_vrfs = set()
        setattr(cls, "routers", [])
        setattr(cls, "hostnames", [])
        setattr(cls, "vrfs", [])
        setattr(cls, "display_vrfs", [])

        for definition in input_params:
            # Validate each router config against Router() model/schema
            router = Router(**definition)

            # Set a class attribute for each router so each router's
            # attributes can be accessed with `devices.router_hostname`
            setattr(cls, router.name, router)

            # Add router-level attributes (assumed to be unique) to
            # class lists, e.g. so all hostnames can be accessed as a
            # list with `devices.hostnames`, same for all router
            # classes, for when iteration over all routers is required.
            cls.hostnames.append(router.name)
            cls.routers.append(router)

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
                    setattr(
                        cls,
                        "default_vrf",
                        {"name": vrf.name, "display_name": vrf.display_name},
                    )

        # Convert the de-duplicated sets to a standard list, add lists
        # as class attributes
        setattr(cls, "vrfs", list(vrfs))
        setattr(cls, "display_vrfs", list(display_vrfs))

        return cls
