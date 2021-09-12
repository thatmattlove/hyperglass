"""Generic command models."""

# Standard Library
import os
import re
from typing import Dict, List, Union, Literal, Optional
from pathlib import Path
from ipaddress import IPv4Network, IPv6Network, ip_network

# Third Party
from pydantic import (
    Field,
    FilePath,
    StrictStr,
    StrictBool,
    PrivateAttr,
    conint,
    validator,
)

# Project
from hyperglass.log import log
from hyperglass.exceptions.private import InputValidationError

# Local
from ..main import HyperglassModel
from ..fields import Action
from ..config.params import Params

IPv4PrefixLength = conint(ge=0, le=32)
IPv6PrefixLength = conint(ge=0, le=128)
IPNetwork = Union[IPv4Network, IPv6Network]
StringOrArray = Union[StrictStr, List[StrictStr]]
Condition = Union[IPv4Network, IPv6Network, StrictStr]
RuleValidation = Union[Literal["ipv4", "ipv6", "pattern"], None]
PassedValidation = Union[bool, None]


class Input(HyperglassModel):
    """Base input field."""

    _type: PrivateAttr
    description: StrictStr

    @property
    def is_select(self) -> bool:
        """Determine if this field is a select field."""
        return self._type == "select"

    @property
    def is_text(self) -> bool:
        """Determine if this field is an input/text field."""
        return self._type == "text"


class Text(Input):
    """Text/input field model."""

    _type: PrivateAttr = PrivateAttr("text")
    validation: Optional[StrictStr]


class Option(HyperglassModel):
    """Select option model."""

    name: Optional[StrictStr]
    description: Optional[StrictStr]
    value: StrictStr


class Select(Input):
    """Select field model."""

    _type: PrivateAttr = PrivateAttr("select")
    options: List[Option]


class Rule(HyperglassModel, allow_population_by_field_name=True):
    """Base rule."""

    _validation: RuleValidation = PrivateAttr()
    _passed: PassedValidation = PrivateAttr(None)
    condition: Condition
    action: Action = Action("permit")
    commands: List[str] = Field([], alias="command")

    @validator("commands", pre=True, allow_reuse=True)
    def validate_commands(cls, value: Union[str, List[str]]) -> List[str]:
        """Ensure commands is a list."""
        if isinstance(value, str):
            return [value]
        return value

    def validate_target(self, target: str) -> bool:
        """Validate a query target (Placeholder signature)."""
        raise NotImplementedError(
            f"{self._validation} rule does not implement a 'validate_target()' method"
        )


class RuleWithIP(Rule):
    """Base IP-based rule."""

    _family: PrivateAttr
    condition: IPNetwork
    allow_reserved: StrictBool = False
    allow_unspecified: StrictBool = False
    allow_loopback: StrictBool = False
    ge: int
    le: int

    def membership(self, target: IPNetwork, network: IPNetwork) -> bool:
        """Check if IP address belongs to network."""
        log.debug("Checking membership of {} for {}", str(target), str(network))
        if (
            network.network_address <= target.network_address
            and network.broadcast_address >= target.broadcast_address
        ):
            log.debug("{} is a member of {}", target, network)
            return True
        return False

    def in_range(self, target: IPNetwork) -> bool:
        """Verify if target prefix length is within ge/le threshold."""
        if target.prefixlen <= self.le and target.prefixlen >= self.ge:
            log.debug("{} is in range {}-{}", target, self.ge, self.le)
            return True

        return False

    def validate_target(self, target: str) -> bool:
        """Validate an IP address target against this rule's conditions."""
        try:
            # Attempt to use IP object factory to create an IP address object
            valid_target = ip_network(target)

        except ValueError as err:
            raise InputValidationError(error=str(err), target=target)

        is_member = self.membership(valid_target, self.condition)
        in_range = self.in_range(valid_target)

        if all((is_member, in_range, self.action == "permit")):
            self._passed = True
            return True

        elif is_member and not in_range:
            self._passed = False
            raise InputValidationError(
                error="Prefix-length is not within range {ge}-{le}",
                target=target,
                ge=self.ge,
                le=self.le,
            )

        elif is_member and self.action == "deny":
            self._passed = False
            raise InputValidationError(
                error="Member of denied network '{network}'",
                target=target,
                network=str(self.condition),
            )

        return False


class RuleWithIPv4(RuleWithIP):
    """A rule by which to evaluate an IPv4 target."""

    _family: PrivateAttr = PrivateAttr("ipv4")
    _validation: RuleValidation = PrivateAttr("ipv4")
    condition: IPv4Network
    ge: IPv4PrefixLength = 0
    le: IPv4PrefixLength = 32


class RuleWithIPv6(RuleWithIP):
    """A rule by which to evaluate an IPv6 target."""

    _family: PrivateAttr = PrivateAttr("ipv6")
    _validation: RuleValidation = PrivateAttr("ipv6")
    condition: IPv6Network
    ge: IPv6PrefixLength = 0
    le: IPv6PrefixLength = 128


class RuleWithPattern(Rule):
    """A rule validated by a regular expression pattern."""

    _validation: RuleValidation = PrivateAttr("pattern")
    condition: StrictStr

    def validate_target(self, target: str) -> str:
        """Validate a string target against configured regex patterns."""

        if self.condition == "*":
            pattern = re.compile(".+", re.IGNORECASE)
        else:
            pattern = re.compile(self.condition, re.IGNORECASE)

        is_match = pattern.match(target)
        if is_match and self.action == "permit":
            self._passed = True
            return True
        elif is_match and self.action == "deny":
            self._passed = False
            raise InputValidationError(target=target, error="Denied")

        return False


class RuleWithoutValidation(Rule):
    """A rule with no validation."""

    _validation: RuleValidation = PrivateAttr(None)
    condition: None

    def validate_target(self, target: str) -> Literal[True]:
        """Don't validate a target. Always returns `True`."""
        self._passed = True
        return True


Rules = Union[RuleWithIPv4, RuleWithIPv6, RuleWithPattern, RuleWithoutValidation]


class Directive(HyperglassModel):
    """A directive contains commands that can be run on a device, as long as defined rules are met."""

    id: StrictStr
    name: StrictStr
    rules: List[Rules]
    field: Union[Text, Select, None]
    info: Optional[FilePath]
    plugins: List[StrictStr] = []
    groups: List[
        StrictStr
    ] = []  # TODO: Flesh this out. Replace VRFs, but use same logic in React to filter available commands for multi-device queries.

    def validate_target(self, target: str) -> bool:
        """Validate a target against all configured rules."""
        for rule in self.rules:
            valid = rule.validate_target(target)
            if valid is True:
                return True
            continue
        raise InputValidationError(error="No matched validation rules", target=target)

    @property
    def field_type(self) -> Literal["text", "select", None]:
        """Get the linked field type."""

        if self.field.is_select:
            return "select"
        elif self.field.is_text or self.field.is_ip:
            return "text"
        return None

    @validator("plugins")
    def validate_plugins(cls: "Directive", plugins: List[str]) -> List[str]:
        """Validate and register configured plugins."""
        plugin_dir = Path(os.environ["hyperglass_directory"]) / "plugins"
        if plugin_dir.exists():
            # Path objects whose file names match configured file names, should work
            # whether or not file extension is specified.
            matching_plugins = (
                f
                for f in plugin_dir.iterdir()
                if f.name.split(".")[0] in (p.split(".")[0] for p in plugins)
            )
            return [str(f) for f in matching_plugins]
        return []

    def frontend(self, params: Params) -> Dict:
        """Prepare a representation of the directive for the UI."""

        value = {
            "id": self.id,
            "name": self.name,
            "field_type": self.field_type,
            "groups": self.groups,
            "description": self.field.description,
            "info": None,
        }

        if self.info is not None:
            with self.info.open() as md:
                value["info"] = {
                    "enable": True,
                    "params": params.content_params(),
                    "content": md.read(),
                }

        if self.field.is_select:
            value["options"] = [
                o.export_dict() for o in self.field.options if o is not None
            ]

        return value
