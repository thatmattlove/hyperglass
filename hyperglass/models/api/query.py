"""Input query validation model."""

# Standard Library
import json
import hashlib
import secrets
from typing import Optional
from datetime import datetime

# Third Party
from pydantic import BaseModel, StrictStr, constr, validator

# Project
from hyperglass.log import log
from hyperglass.util import snake_to_camel, repr_from_attrs
from hyperglass.state import use_state
from hyperglass.exceptions.public import (
    InputInvalid,
    QueryTypeNotFound,
    QueryLocationNotFound,
)
from hyperglass.exceptions.private import InputValidationError

# Local
from ..config.devices import Device

(TEXT := use_state("params").web.text)


class Query(BaseModel):
    """Validation model for input query parameters."""

    # Device `name` field
    query_location: StrictStr
    # Directive `id` field
    query_type: StrictStr
    # Directive `groups` member
    query_group: Optional[StrictStr] = None
    query_target: constr(strip_whitespace=True, min_length=1)

    class Config:
        """Pydantic model configuration."""

        extra = "allow"
        alias_generator = snake_to_camel
        fields = {
            "query_location": {
                "title": TEXT.query_location,
                "description": "Router/Location Name",
                "example": "router01",
            },
            "query_type": {
                "title": TEXT.query_type,
                "description": "Type of Query to Execute",
                "example": "bgp_route",
            },
            "query_group": {
                "title": TEXT.query_group,
                "description": "Routing Table/VRF",
                "example": "default",
            },
            "query_target": {
                "title": TEXT.query_target,
                "description": "IP Address, Community, or AS Path",
                "example": "1.1.1.0/24",
            },
        }
        schema_extra = {"x-code-samples": [{"lang": "Python", "source": "print('stuff')"}]}

    def __init__(self, **kwargs):
        """Initialize the query with a UTC timestamp at initialization time."""
        super().__init__(**kwargs)
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        state = use_state()
        self._state = state
        query_directives = self.device.directives.matching(self.query_type)
        if len(query_directives) < 1:
            raise QueryTypeNotFound(query_type=self.query_type)
        self.directive = query_directives[0]
        try:
            self.validate_query_target()
        except InputValidationError as err:
            raise InputInvalid(**err.kwargs)

    def __repr__(self):
        """Represent only the query fields."""
        return repr_from_attrs(self, self.__config__.fields.keys())

    def __str__(self) -> str:
        """Alias __str__ to __repr__."""
        return repr(self)

    def digest(self):
        """Create SHA256 hash digest of model representation."""
        return hashlib.sha256(repr(self).encode()).hexdigest()

    def random(self):
        """Create a random string to prevent client or proxy caching."""
        return hashlib.sha256(
            secrets.token_bytes(8) + repr(self).encode() + secrets.token_bytes(8)
        ).hexdigest()

    def validate_query_target(self):
        """Validate a query target after all fields/relationships havebeen initialized."""
        self.directive.validate_target(self.query_target)
        log.debug("Validation passed for query {!r}", self)

    @property
    def summary(self):
        """Create abbreviated representation of instance."""
        items = (
            f"query_location={self.query_location}",
            f"query_type={self.query_type}",
            f"query_group={self.query_group}",
            f"query_target={self.query_target!s}",
        )
        return f'Query({", ".join(items)})'

    @property
    def device(self) -> Device:
        """Get this query's device object by query_location."""
        return self._state.devices[self.query_location]

    def export_dict(self, pretty=False):
        """Create dictionary representation of instance."""

        if pretty:
            items = {
                "query_location": self.device.name,
                "query_type": self.query.display_name,
                "query_group": self.query_group,
                "query_target": str(self.query_target),
            }
        else:
            items = {
                "query_location": self.query_location,
                "query_type": self.query_type,
                "query_group": self.query_group,
                "query_target": str(self.query_target),
            }
        return items

    def export_json(self):
        """Create JSON representation of instance."""
        return json.dumps(self.export_dict(), default=str)

    @validator("query_type")
    def validate_query_type(cls, value):
        """Ensure a requested query type exists."""
        devices = use_state("devices")
        if any((device.has_directives(value) for device in devices)):
            return value

        raise QueryTypeNotFound(name=value)

    @validator("query_location")
    def validate_query_location(cls, value):
        """Ensure query_location is defined."""

        devices = use_state("devices")

        if not devices.valid_id_or_name(value):
            raise QueryLocationNotFound(location=value)

        return value
