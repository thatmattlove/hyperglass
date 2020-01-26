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
from hyperglass.exceptions import InputInvalid
from hyperglass.models.types import SupportedQuery
from hyperglass.models.validators import validate_aspath
from hyperglass.models.validators import validate_community
from hyperglass.models.validators import validate_ip


class Query(BaseModel):
    """Validation model for input query parameters."""

    query_location: StrictStr
    query_type: SupportedQuery
    query_target: StrictStr
    query_vrf: StrictStr

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
                field=params.branding.text.query_location,
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
        device = getattr(devices, values["query_location"])
        default_vrf = "default"
        if value is not None and value != default_vrf:
            for vrf in device.vrfs:
                if value == vrf.name:
                    value = vrf.name
                elif value == vrf.display_name:
                    value = vrf.name
                else:
                    raise InputInvalid(
                        params.messages.vrf_not_associated,
                        level="warning",
                        vrf_name=vrf.display_name,
                        device_name=device.display_name,
                    )
        if value is None:
            value = default_vrf
        return value

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
        validate_func = validator_map[query_type]

        return validate_func(value, query_type)
