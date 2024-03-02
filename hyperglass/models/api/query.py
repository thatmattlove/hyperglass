"""Input query validation model."""

# Standard Library
import typing as t
import hashlib
import secrets
from datetime import datetime

# Third Party
from pydantic import BaseModel, constr, validator

# Project
from hyperglass.log import log
from hyperglass.util import snake_to_camel, repr_from_attrs
from hyperglass.state import use_state
from hyperglass.plugins import InputPluginManager
from hyperglass.exceptions.public import InputInvalid, QueryTypeNotFound, QueryLocationNotFound
from hyperglass.exceptions.private import InputValidationError

# Local
from ..config.devices import Device


QueryLocation = constr(strip_whitespace=True, strict=True, min_length=1)
QueryTarget = constr(strip_whitespace=True, min_length=1)
QueryType = constr(strip_whitespace=True, strict=True, min_length=1)


class Query(BaseModel):
    """Validation model for input query parameters."""

    query_location: QueryLocation  # Device `name` field
    query_target: t.Union[t.List[QueryTarget], QueryTarget]
    query_type: QueryType  # Directive `id` field

    class Config:
        """Pydantic model configuration."""

        extra = "allow"
        alias_generator = snake_to_camel
        allow_population_by_field_name = True

    def __init__(self, **data) -> None:
        """Initialize the query with a UTC timestamp at initialization time."""
        super().__init__(**data)
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        state = use_state()
        self._state = state

        query_directives = self.device.directives.matching(self.query_type)

        if len(query_directives) < 1:
            raise QueryTypeNotFound(query_type=self.query_type)

        self.directive = query_directives[0]

        self._input_plugin_manager = InputPluginManager()

        self.query_target = self.transform_query_target()

        try:
            self.validate_query_target()
        except InputValidationError as err:
            raise InputInvalid(**err.kwargs) from err

    def __repr__(self) -> str:
        """Represent only the query fields."""
        return repr_from_attrs(self, ("query_location", "query_type", "query_target"))

    def __str__(self) -> str:
        """Alias __str__ to __repr__."""
        return repr(self)

    def digest(self) -> str:
        """Create SHA256 hash digest of model representation."""
        return hashlib.sha256(repr(self).encode()).hexdigest()

    def random(self) -> str:
        """Create a random string to prevent client or proxy caching."""
        return hashlib.sha256(
            secrets.token_bytes(8) + repr(self).encode() + secrets.token_bytes(8)
        ).hexdigest()

    def validate_query_target(self) -> None:
        """Validate a query target after all fields/relationships have been initialized."""
        # Run config/rule-based validations.
        self.directive.validate_target(self.query_target)
        # Run plugin-based validations.
        self._input_plugin_manager.validate(query=self)
        log.debug("Validation passed for query {!r}", self)

    def transform_query_target(self) -> QueryTarget:
        """Transform a query target based on defined plugins."""
        return self._input_plugin_manager.transform(query=self)

    def dict(self) -> t.Dict[str, t.Union[t.List[str], str]]:
        """Include only public fields."""
        return super().dict(include={"query_location", "query_target", "query_type"})

    @property
    def device(self) -> Device:
        """Get this query's device object by query_location."""
        return self._state.devices[self.query_location]

    @validator("query_location")
    def validate_query_location(cls, value):
        """Ensure query_location is defined."""

        devices = use_state("devices")

        if not devices.valid_id_or_name(value):
            raise QueryLocationNotFound(location=value)

        return value

    @validator("query_type")
    def validate_query_type(cls, value: t.Any):
        """Ensure a requested query type exists."""
        devices = use_state("devices")
        if any((device.has_directives(value) for device in devices)):
            return value

        raise QueryTypeNotFound(query_type=value)
