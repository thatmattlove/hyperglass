"""Input query validation model."""

# Standard Library
import json
import hashlib
import secrets
from datetime import datetime

# Third Party
from pydantic import BaseModel, StrictStr, constr, validator

# Project
from hyperglass.exceptions import InputInvalid
from hyperglass.configuration import params, devices

# Local
from .types import SupportedQuery
from .validators import (
    validate_ip,
    validate_aspath,
    validate_community_input,
    validate_community_select,
)


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
    query_vrf: StrictStr
    query_target: constr(strip_whitespace=True, min_length=1)

    class Config:
        """Pydantic model configuration."""

        extra = "allow"
        fields = {
            "query_location": {
                "title": params.web.text.query_location,
                "description": "Router/Location Name",
                "example": "router01",
            },
            "query_type": {
                "title": params.web.text.query_type,
                "description": "Type of Query to Execute",
                "example": "bgp_route",
            },
            "query_vrf": {
                "title": params.web.text.query_vrf,
                "description": "Routing Table/VRF",
                "example": "default",
            },
            "query_target": {
                "title": params.web.text.query_target,
                "description": "IP Address, Community, or AS Path",
                "example": "1.1.1.0/24",
            },
        }
        schema_extra = {
            "x-code-samples": [{"lang": "Python", "source": "print('stuff')"}]
        }

    def __init__(self, **kwargs):
        """Initialize the query with a UTC timestamp at initialization time."""
        super().__init__(**kwargs)
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        """Represent only the query fields."""
        return (
            f"Query(query_location={str(self.query_location)}, "
            f"query_type={str(self.query_type)}, query_vrf={str(self.query_vrf)}, "
            f"query_target={str(self.query_target)})"
        )

    def digest(self):
        """Create SHA256 hash digest of model representation."""
        return hashlib.sha256(repr(self).encode()).hexdigest()

    def random(self):
        """Create a random string to prevent client or proxy caching."""
        return hashlib.sha256(
            secrets.token_bytes(8) + repr(self).encode() + secrets.token_bytes(8)
        ).hexdigest()

    @property
    def summary(self):
        """Create abbreviated representation of instance."""
        items = (
            f"query_location={self.query_location}",
            f"query_type={self.query_type}",
            f"query_vrf={self.query_vrf.name}",
            f"query_target={str(self.query_target)}",
        )
        return f'Query({", ".join(items)})'

    @property
    def device(self):
        """Get this query's device object by query_location."""
        return devices[self.query_location]

    @property
    def query(self):
        """Get this query's configuration object."""
        return params.queries[self.query_type]

    def export_dict(self, pretty=False):
        """Create dictionary representation of instance."""
        if pretty:
            items = {
                "query_location": self.device.display_name,
                "query_type": self.query.display_name,
                "query_vrf": self.query_vrf.display_name,
                "query_target": str(self.query_target),
            }
        else:
            items = {
                "query_location": self.query_location,
                "query_type": self.query_type,
                "query_vrf": self.query_vrf.name,
                "query_target": str(self.query_target),
            }
        return items

    def export_json(self):
        """Create JSON representation of instance."""
        return json.dumps(self.export_dict(), default=str)

    @validator("query_type")
    def validate_query_type(cls, value):
        """Ensure query_type is enabled.

        Arguments:
            value {str} -- Query Type

        Raises:
            InputInvalid: Raised if query_type is disabled.

        Returns:
            {str} -- Valid query_type
        """
        query = params.queries[value]
        if not query.enable:
            raise InputInvalid(
                params.messages.feature_not_enabled,
                level="warning",
                feature=query.display_name,
            )
        return value

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
                level="warning",
                input=value,
                field=params.web.text.query_location,
            )
        return value

    @validator("query_vrf")
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
        device = devices[values["query_location"]]
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

    @validator("query_target")
    def validate_query_target(cls, value, values):
        """Validate query target value based on query_type."""

        query_type = values["query_type"]
        value = value.strip()

        # Use relevant function based on query_type.
        validator_map = {
            "bgp_aspath": validate_aspath,
            "bgp_community": validate_community_input,
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

        if params.queries.bgp_community.mode == "select":
            validator_map["bgp_community"] = validate_community_select

        validate_func = validator_map[query_type]
        validate_args = validator_args_map[query_type]

        return validate_func(*validate_args)
