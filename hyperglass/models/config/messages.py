"""Validate error message configuration variables."""

# Third Party
from pydantic import Field, StrictStr

# Local
from ..main import HyperglassModel


class Messages(HyperglassModel):
    """Validation model for params.messages."""

    no_input: StrictStr = Field(
        "{field} must be specified.",
        title="No Input",
        description="Displayed when no a required field is not specified. `{field}` may be used to display the `display_name` of the field that was omitted.",
    )
    acl_denied: StrictStr = Field(
        "{target} is a member of {denied_network}, which is not allowed.",
        title="ACL - Denied",
        description="Displayed when a query target is explicitly denied by a matched VRF's ACL entry. `{target}` and `{denied_network}` may be used to display the denied query target and the ACL entry that caused it to be denied.",
    )
    acl_not_allowed: StrictStr = Field(
        "{target} is not allowed.",
        title="ACL - Not Allowed",
        description="Displayed when a query target is implicitly denied by a matched VRF's ACL. `{target}` may be used to display the denied query target.",
    )
    feature_not_enabled: StrictStr = Field(
        "{feature} is not enabled.",
        title="Feature Not Enabled",
        description="Displayed when a query type is submitted that is not supported or disabled. The hyperglass UI performs validation of supported query types prior to submitting any requests, so this is primarily relevant to the hyperglass API. `{feature}` may be used to display the disabled feature.",
    )
    invalid_input: StrictStr = Field(
        "{target} is not a valid {query_type} target.",
        title="Invalid Input",
        description="Displayed when a query target's value is invalid in relation to the corresponding query type. `{target}` and `{query_type}` maybe used to display the invalid target and corresponding query type.",
    )
    invalid_field: StrictStr = Field(
        "{input} is an invalid {field}.",
        title="Invalid Field",
        description="Displayed when a query field contains an invalid or unsupported value. `{input}` and `{field}` may be used to display the invalid input value and corresponding field name.",
    )
    general: StrictStr = Field(
        "Something went wrong.",
        title="General Error",
        description="Displayed when generalized errors occur. Seeing this error message may indicate a bug in hyperglass, as most other errors produced are highly contextual. If you see this in the wild, try enabling [debug mode](/fixme) and review the logs to pinpoint the source of the error.",
    )
    request_timeout: StrictStr = Field(
        "Request timed out.",
        title="Request Timeout",
        description="Displayed when the [request_timeout](/fixme) time expires.",
    )
    connection_error: StrictStr = Field(
        "Error connecting to {device_name}: {error}",
        title="Displayed when hyperglass is unable to connect to a configured device. Usually, this indicates a configuration error. `{device_name}` and `{error}` may be used to display the device in question and the specific connection error.",
    )
    authentication_error: StrictStr = Field(
        "Authentication error occurred.",
        title="Authentication Error",
        description="Displayed when hyperglass is unable to authenticate to a configured device. Usually, this indicates a configuration error.",
    )
    no_response: StrictStr = Field(
        "No response.",
        title="No Response",
        description="Displayed when hyperglass can connect to a device, but no output able to be read. Seeing this error may indicate a bug in hyperglas or one of its dependencies. If you see this in the wild, try enabling [debug mode](/fixme) and review the logs to pinpoint the source of the error.",
    )
    vrf_not_associated: StrictStr = Field(
        "VRF {vrf_name} is not associated with {device_name}.",
        title="VRF Not Associated",
        description="Displayed when a query request's VRF field value contains a VRF that is not configured or associated with the corresponding location/device. The hyperglass UI automatically filters out VRFs that are not configured on a selected device, so this error is most likely to appear when using the hyperglass API. `{vrf_name}` and `{device_name}` may be used to display the VRF in question and corresponding device.",
    )
    vrf_not_found: StrictStr = Field(
        "VRF {vrf_name} is not defined.",
        title="VRF Not Found",
        description="Displayed when a query VRF is not configured on any devices. The hyperglass UI only shows configured VRFs, so this error is most likely to appear when using the hyperglass API. `{vrf_name}` may be used to display the VRF in question.",
    )
    no_output: StrictStr = Field(
        "The query completed, but no matching results were found.",
        title="No Output",
        description="Displayed when hyperglass can connect to a device and execute a query, but the response is empty.",
    )
    parsing_error: StrictStr = Field(
        "An error occurred while parsing the query output.",
        title="Parsing Error",
        description="Displayed when hyperglass can connect to a device and execute a query, but the response cannot be parsed.",
    )

    class Config:
        """Pydantic model configuration."""

        title = "Messages"
        description = "Customize almost all user-facing UI & API messages."
        schema_extra = {"level": 2}
