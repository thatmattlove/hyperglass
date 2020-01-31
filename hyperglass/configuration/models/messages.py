"""Validate error message configuration variables."""

# Third Party Imports
from pydantic import StrictStr

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Messages(HyperglassModel):
    """Validation model for params.messages."""

    no_input: StrictStr = "{field} must be specified."
    acl_denied: StrictStr = "{target} is a member of {denied_network}, which is not allowed."
    acl_not_allowed: StrictStr = "{target} is not allowed."
    max_prefix: StrictStr = (
        "Prefix length must be shorter than /{max_length}. {target} is too specific."
    )
    requires_ipv6_cidr: StrictStr = (
        "{device_name} requires IPv6 BGP lookups to be in CIDR notation."
    )
    feature_not_enabled: StrictStr = "{feature} is not enabled for {device_name}."
    invalid_input: StrictStr = "{target} is not a valid {query_type} target."
    invalid_field: StrictStr = "{input} is an invalid {field}."
    general: StrictStr = "Something went wrong."
    directed_cidr: StrictStr = "{query_type} queries can not be in CIDR format."
    request_timeout: StrictStr = "Request timed out."
    connection_error: StrictStr = "Error connecting to {device_name}: {error}"
    authentication_error: StrictStr = "Authentication error occurred."
    noresponse_error: StrictStr = "No response."
    vrf_not_associated: StrictStr = "VRF {vrf_name} is not associated with {device_name}."
    vrf_not_found: StrictStr = "VRF {vrf_name} is not defined."
    no_matching_vrfs: StrictStr = "No VRFs in Common"
    no_output: StrictStr = "No output."
