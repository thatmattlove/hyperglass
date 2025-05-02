"""Validate error message configuration variables."""

# Third Party
from pydantic import Field, ConfigDict

# Local
from ..main import HyperglassModel


class Messages(HyperglassModel):
    """Validation model for params.messages."""

    model_config = ConfigDict(
        title="Messages",
        description="Customize almost all user-facing UI & API messages.",
        json_schema_extra={"level": 2},
    )

    no_input: str = Field(
        "{field} must be specified.",
        title="No Input",
        description="Displayed when no a required field is not specified. `{field}` may be used to display the `display_name` of the field that was omitted.",
    )
    target_not_allowed: str = Field(
        "{target} is not allowed.",
        title="Target Not Allowed",
        description="Displayed when a query target is implicitly denied by a configured rule. `{target}` will be used to display the denied query target.",
    )
    feature_not_enabled: str = Field(
        "{feature} is not enabled.",
        title="Feature Not Enabled",
        description="Displayed when a query type is submitted that is not supported or disabled. The hyperglass UI performs validation of supported query types prior to submitting any requests, so this is primarily relevant to the hyperglass API. `{feature}` may be used to display the disabled feature.",
    )
    invalid_input: str = Field(
        "{target} is not valid.",
        title="Invalid Input",
        description="Displayed when a query target's value is invalid in relation to the corresponding query type. `{target}` may be used to display the invalid target.",
    )
    invalid_query: str = Field(
        "{target} is not a valid {query_type} target.",
        title="Invalid Query",
        description="Displayed when a query target's value is invalid in relation to the corresponding query type. `{target}` and `{query_type}` may be used to display the invalid target and corresponding query type.",
    )
    invalid_field: str = Field(
        "{input} is an invalid {field}.",
        title="Invalid Field",
        description="Displayed when a query field contains an invalid or unsupported value. `{input}` and `{field}` may be used to display the invalid input value and corresponding field name.",
    )
    general: str = Field(
        "Something went wrong.",
        title="General Error",
        description="Displayed when generalized errors occur. Seeing this error message may indicate a bug in hyperglass, as most other errors produced are highly contextual. If you see this in the wild, try enabling [debug mode](/fixme) and review the logs to pinpoint the source of the error.",
    )
    not_found: str = Field(
        "{type} '{name}' not found.",
        title="Not Found",
        description="Displayed when an object property does not exist in the configuration. `{type}` corresponds to a user-friendly name of the object type (for example, 'Device'), `{name}` corresponds to the object name that was not found.",
    )
    request_timeout: str = Field(
        "Request timed out.",
        title="Request Timeout",
        description="Displayed when the [request_timeout](/fixme) time expires.",
    )
    connection_error: str = Field(
        "Error connecting to {device_name}: {error}",
        title="Displayed when hyperglass is unable to connect to a configured device. Usually, this indicates a configuration error. `{device_name}` and `{error}` may be used to display the device in question and the specific connection error.",
    )
    authentication_error: str = Field(
        "Authentication error occurred.",
        title="Authentication Error",
        description="Displayed when hyperglass is unable to authenticate to a configured device. Usually, this indicates a configuration error.",
    )
    no_response: str = Field(
        "No response.",
        title="No Response",
        description="Displayed when hyperglass can connect to a device, but no output able to be read. Seeing this error may indicate a bug in hyperglas or one of its dependencies. If you see this in the wild, try enabling [debug mode](/fixme) and review the logs to pinpoint the source of the error.",
    )
    no_output: str = Field(
        "The query completed, but no matching results were found.",
        title="No Output",
        description="Displayed when hyperglass can connect to a device and execute a query, but the response is empty.",
    )

    def has(self, attr: str) -> bool:
        """Determine if message type exists in Messages model."""
        return attr in self.model_dump().keys()

    def __getitem__(self, attr: str) -> str:
        """Make messages subscriptable."""

        if not self.has(attr):
            raise KeyError(f"'{attr}' does not exist on Messages model")
        return getattr(self, attr)
