"""
Defines models for Messages config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Messages(HyperglassModel):
    """Class model for params.messages"""

    no_input: str = "{field} must be specified."
    acl_denied: str = "{target} is a member of {denied_network}, which is not allowed."
    acl_not_allowed: str = "{target} is not allowed."
    max_prefix: str = (
        "Prefix length must be shorter than /{max_length}. {target} is too specific."
    )
    requires_ipv6_cidr: str = (
        "{device_name} requires IPv6 BGP lookups to be in CIDR notation."
    )
    feature_not_enabled: str = "{feature} is not enabled for {device_name}."
    invalid_input: str = "{target} is not a valid {query_type} target."
    invalid_field: str = "{input} is an invalid {field}."
    general: str = "Something went wrong."
    directed_cidr: str = "{query_type} queries can not be in CIDR format."
    request_timeout: str = "Request timed out."
    connection_error: str = "Error connecting to {device_name}: {error}"
    authentication_error: str = "Authentication error occurred."
    noresponse_error: str = "No response."
    vrf_not_associated: str = "VRF {vrf_name} is not associated with {device_name}."
    no_matching_vrfs: str = "No VRFs in Common"
    no_output: str = "No output."
