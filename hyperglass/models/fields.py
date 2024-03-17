"""Custom Pydantic Fields/Types."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import AfterValidator, BeforeValidator

IntFloat = t.TypeVar("IntFloat", int, float)
J = t.TypeVar("J")

SupportedDriver = t.Literal["netmiko", "hyperglass_agent"]
HttpAuthMode = t.Literal["basic", "api_key"]
HttpProvider = t.Literal["msteams", "slack", "generic"]
LogFormat = t.Literal["text", "json"]
Primitives = t.Union[None, float, int, bool, str]
JsonValue = t.Union[J, t.Sequence[J], t.Dict[str, J]]
ActionValue = t.Literal["permit", "deny"]
HttpMethodValue = t.Literal[
    "CONNECT",
    "DELETE",
    "GET",
    "HEAD",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "TRACE",
]


def validate_uri(value: str) -> str:
    """Ensure URI string contains a leading forward-slash."""
    uri_regex = re.compile(r"^(\/.*)$")
    match = uri_regex.fullmatch(value)
    if not match:
        raise ValueError("Invalid format. A URI must begin with a forward slash, e.g. '/example'")
    return match.group()


def validate_action(value: str) -> ActionValue:
    """Ensure action is an allowed value or acceptable alias."""
    permits = ("permit", "allow", "accept")
    denies = ("deny", "block", "reject")
    value = value.strip().lower()
    if value in permits:
        return "permit"
    if value in denies:
        return "deny"

    raise ValueError("Action must be one of '{}'".format(", ".join((*permits, *denies))))


AnyUri = t.Annotated[str, AfterValidator(validate_uri)]
Action = t.Annotated[ActionValue, AfterValidator(validate_action)]
HttpMethod = t.Annotated[HttpMethodValue, BeforeValidator(str.upper)]
