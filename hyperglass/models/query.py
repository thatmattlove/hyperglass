"""Input query validation model."""

# Standard Library Imports
import hashlib

# Third Party Imports
from pydantic import BaseModel
from pydantic import StrictStr
from pydantic import validator

# Project Imports
from hyperglass.configuration import devices
from hyperglass.configuration import params
from hyperglass.configuration.models.vrfs import Vrf
from hyperglass.exceptions import InputInvalid
from hyperglass.models.types import SupportedQuery
from hyperglass.models.validators import validate_aspath
from hyperglass.models.validators import validate_community
from hyperglass.models.validators import validate_ip


def get_vrf_object(vrf_name):
    """Match VRF object from VRF name.

    Arguments:
        vrf_name {str} -- VRF name

    Raises:
        InputInvalid: Raised if no VRF is matched.

    Returns:
        {object} -- Valid VRF object
    """
    matched = None
    for vrf_obj in devices.vrf_objects:
        if vrf_name is not None:
            if vrf_name == vrf_obj.name or vrf_name == vrf_obj.display_name:
                matched = vrf_obj
                break
        elif vrf_name is None:
            if vrf_obj.name == "default":
                matched = vrf_obj
                break
    if matched is None:
        raise InputInvalid(params.messages.vrf_not_found, vrf_name=vrf_name)
    return matched


class Query(BaseModel):
    """Validation model for input query parameters."""

    query_location: StrictStr
    query_type: SupportedQuery
    query_vrf: Vrf
    query_target: StrictStr

    def digest(self):
        """Create SHA256 hash digest of model representation."""
        return hashlib.sha256(repr(self).encode()).hexdigest()

    @validator("query_location", pre=True, always=True)
    def validate_query_location(cls, value):
        """Ensure query_location is defined.

        Arguments:
            value {str} -- Unvalidated query_location

        Raises:
            InputInvalid: Raised if query_location is not defined.

        Returns:
            {str} -- Valid query_location
        """
        if value not in devices.hostnames:
            raise InputInvalid(
                params.messages.invalid_field,
                level="warning",
                input=value,
                field=params.web.text.query_location,
            )
        return value

    @validator("query_vrf", always=True, pre=True)
    def validate_query_vrf(cls, value, values):
        """Ensure query_vrf is defined.

        Arguments:
            value {str} -- Unvalidated query_vrf

        Raises:
            InputInvalid: Raised if query_vrf is not defined.

        Returns:
            {str} -- Valid query_vrf
        """
        vrf_object = get_vrf_object(value)
        device = getattr(devices, values["query_location"])
        device_vrf = None
        for vrf in device.vrfs:
            if vrf == vrf_object:
                device_vrf = vrf
                break
        if device_vrf is None:
            raise InputInvalid(
                params.messages.vrf_not_associated,
                vrf_name=vrf_object.display_name,
                device_name=device.display_name,
            )
        return device_vrf

    @validator("query_target", always=True)
    def validate_query_target(cls, value, values):
        """Validate query target value based on query_type."""

        query_type = values["query_type"]

        # Use relevant function based on query_type.
        validator_map = {
            "bgp_aspath": validate_aspath,
            "bgp_community": validate_community,
            "bgp_route": validate_ip,
            "ping": validate_ip,
            "traceroute": validate_ip,
        }
        validator_args_map = {
            "bgp_aspath": (value,),
            "bgp_community": (value,),
            "bgp_route": (value, values["query_type"], values["query_vrf"]),
            "ping": (value, values["query_type"], values["query_vrf"]),
            "traceroute": (value, values["query_type"], values["query_vrf"]),
        }
        validate_func = validator_map[query_type]
        validate_args = validator_args_map[query_type]

        return validate_func(*validate_args)
