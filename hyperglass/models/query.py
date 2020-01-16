"""Input query validation model."""

# Standard Library Imports
import operator
from typing import Optional

# Third Party Imports
from pydantic import BaseModel
from pydantic import StrictStr
from pydantic import validator

# Project Imports
from hyperglass.configuration import devices
from hyperglass.configuration import params
from hyperglass.constants import Supported
from hyperglass.exceptions import InputInvalid


class Query(BaseModel):
    """Validation model for input query parameters."""

    query_location: StrictStr
    query_type: StrictStr
    query_vrf: Optional[StrictStr]
    query_target: StrictStr

    @validator("query_location")
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
                alert="warning",
                input=value,
                field=params.branding.text.query_location,
            )
        return value

    @validator("query_type")
    def validate_query_type(cls, value):
        """Ensure query_type is supported.

        Arguments:
            value {str} -- Unvalidated query_type

        Raises:
            InputInvalid: Raised if query_type is not supported.

        Returns:
            {str} -- Valid query_type
        """
        if value not in Supported.query_types:
            raise InputInvalid(
                params.messages.invalid_field,
                alert="warning",
                input=value,
                field=params.branding.text.query_type,
            )
        else:
            enabled = operator.attrgetter(f"{value}.enable")(params.features)
            if not enabled:
                raise InputInvalid(
                    params.messages.invalid_field,
                    alert="warning",
                    input=value,
                    field=params.branding.text.query_type,
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
                        alert="warning",
                        vrf_name=value,
                        device_name=device.display_name,
                    )
        if value is None:
            value = default_vrf
        return value
