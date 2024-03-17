"""Generic command models."""

# Standard Library
import re
import typing as t
from ipaddress import IPv4Network, IPv6Network, ip_network

# Third Party
from pydantic import (
    Discriminator,
    field_validator,
    Field,
    FilePath,
    IPvAnyNetwork,
    PrivateAttr,
    Tag,
)

# Project
from hyperglass.log import log
from hyperglass.types import Series
from hyperglass.settings import Settings
from hyperglass.exceptions.private import InputValidationError

# Local
from .main import MultiModel, HyperglassModel, HyperglassUniqueModel
from .fields import Action


StringOrArray = t.Union[str, t.List[str]]
Condition = t.Union[IPvAnyNetwork, str]
RuleValidation = t.Union[t.Literal["ipv4", "ipv6", "pattern"], None]
PassedValidation = t.Union[bool, None]
IPFamily = t.Literal["ipv4", "ipv6"]
RuleTypeAttr = t.Literal["ipv4", "ipv6", "pattern", "none"]


class Input(HyperglassModel):
    """Base input field."""

    _type: PrivateAttr
    description: str

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
    validation: t.Optional[str] = None


class Option(HyperglassModel):
    """Select option model."""

    name: t.Optional[str] = None
    description: t.Optional[str] = None
    value: str


class Select(Input):
    """Select field model."""

    _type: PrivateAttr = PrivateAttr("select")
    options: t.List[Option]


class Rule(HyperglassModel):
    """Base rule."""

    _type: RuleTypeAttr = PrivateAttr(Field("none", discriminator="_type"))
    _passed: PassedValidation = PrivateAttr(None)
    condition: Condition
    action: Action = "permit"
    commands: t.List[str] = Field([], alias="command")

    @field_validator("commands", mode="before")
    def validate_commands(cls, value: t.Union[str, t.List[str]]) -> t.List[str]:
        """Ensure commands is a list."""
        if isinstance(value, str):
            return [value]
        return value

    def validate_target(self, target: str, *, multiple: bool) -> bool:
        """Validate a query target (Placeholder signature)."""
        raise NotImplementedError(
            f"{self._type} rule does not implement a 'validate_target()' method"
        )


class RuleWithIP(Rule):
    """Base IP-based rule."""

    condition: IPvAnyNetwork
    allow_reserved: bool = False
    allow_unspecified: bool = False
    allow_loopback: bool = False
    ge: int
    le: int

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        if self.condition.network_address.version == 4:
            self._type = "ipv4"
        else:
            self._type = "ipv6"

    def membership(self, target: IPvAnyNetwork, network: IPvAnyNetwork) -> bool:
        """Check if IP address belongs to network."""
        log.debug("Checking membership of {} for {}", str(target), str(network))
        if (
            network.network_address <= target.network_address
            and network.broadcast_address >= target.broadcast_address
        ):
            log.debug("{} is a member of {}", target, network)
            return True
        return False

    def in_range(self, target: IPvAnyNetwork) -> bool:
        """Verify if target prefix length is within ge/le threshold."""
        if target.prefixlen <= self.le and target.prefixlen >= self.ge:
            log.debug("{} is in range {}-{}", target, self.ge, self.le)
            return True

        return False

    def validate_target(self, target: str, *, multiple: bool) -> bool:
        """Validate an IP address target against this rule's conditions."""

        if isinstance(target, t.List):
            if len(target) > 1:
                self._passed = False
                raise InputValidationError("Target must be a single value")
            target = target[0]

        try:
            # Attempt to use IP object factory to create an IP address object
            valid_target = ip_network(target)

        except ValueError as err:
            raise InputValidationError(error=str(err), target=target) from err

        is_member = self.membership(valid_target, self.condition)
        in_range = self.in_range(valid_target)

        if all((is_member, in_range, self.action == "permit")):
            self._passed = True
            return True

        if is_member and not in_range:
            self._passed = False
            raise InputValidationError(
                error="Prefix-length is not within range {ge}-{le}",
                target=target,
                ge=self.ge,
                le=self.le,
            )

        if is_member and self.action == "deny":
            self._passed = False
            raise InputValidationError(
                error="Member of denied network '{network}'",
                target=target,
                network=str(self.condition),
            )

        return False


class RuleWithIPv4(RuleWithIP):
    """A rule by which to evaluate an IPv4 target."""

    _type: RuleTypeAttr = "ipv4"
    condition: IPv4Network
    ge: int = Field(0, ge=0, le=32)
    le: int = Field(32, ge=0, le=32)


class RuleWithIPv6(RuleWithIP):
    """A rule by which to evaluate an IPv6 target."""

    _type: RuleTypeAttr = "ipv6"
    condition: IPv6Network
    ge: int = Field(0, ge=0, le=128)
    le: int = Field(128, ge=0, le=128)


class RuleWithPattern(Rule):
    """A rule validated by a regular expression pattern."""

    _type: RuleTypeAttr = "pattern"
    condition: str

    def validate_target(self, target: str, *, multiple: bool) -> str:  # noqa: C901
        """Validate a string target against configured regex patterns."""

        def validate_single_value(value: str) -> t.Union[bool, BaseException]:
            if self.condition == "*":
                pattern = re.compile(".+", re.IGNORECASE)
            else:
                pattern = re.compile(self.condition, re.IGNORECASE)
            is_match = pattern.match(value)

            if is_match and self.action == "permit":
                return True
            if is_match and self.action == "deny":
                return InputValidationError(target=value, error="Denied")
            return False

        if isinstance(target, t.List) and multiple:
            for result in (validate_single_value(v) for v in target):
                if isinstance(result, BaseException):
                    self._passed = False
                    raise result
                if result is False:
                    self._passed = False
                    return result
            self._passed = True
            return True

        if isinstance(target, t.List) and not multiple:
            raise InputValidationError("Target must be a single value")

        result = validate_single_value(target)

        if isinstance(result, BaseException):
            self._passed = False
            raise result
        self._passed = result
        return result


class RuleWithoutValidation(Rule):
    """A rule with no validation."""

    _type: RuleTypeAttr = "none"
    condition: None

    def validate_target(self, target: str, *, multiple: bool) -> t.Literal[True]:
        """Don't validate a target. Always returns `True`."""
        self._passed = True
        return True


RuleWithIPv4Type = t.Annotated[RuleWithIPv4, Tag("ipv4")]
RuleWithIPv6Type = t.Annotated[RuleWithIPv6, Tag("ipv6")]
RuleWithPatternType = t.Annotated[RuleWithPattern, Tag("pattern")]
RuleWithoutValidationType = t.Annotated[RuleWithoutValidation, Tag("none")]

# RuleType = t.Union[RuleWithIPv4, RuleWithIPv6, RuleWithPattern, RuleWithoutValidation]
RuleType = t.Union[
    RuleWithIPv4Type,
    RuleWithIPv6Type,
    RuleWithPatternType,
    RuleWithoutValidationType,
]


def type_discriminator(value: t.Any) -> RuleTypeAttr:
    """Pydantic type discriminator."""
    if isinstance(value, dict):
        return value.get("_type")
    return getattr(value, "_type", None)


class Directive(HyperglassUniqueModel, unique_by=("id", "table_output")):
    """A directive contains commands that can be run on a device, as long as defined rules are met."""

    _hyperglass_builtin: bool = PrivateAttr(False)

    id: str
    name: str
    rules: t.List[RuleType] = [
        Field(RuleWithPattern(condition="*"), discriminator=Discriminator(type_discriminator))
    ]
    field: t.Union[Text, Select]
    info: t.Optional[FilePath] = None
    plugins: t.List[str] = []
    table_output: t.Optional[str] = None
    groups: t.List[str] = []
    multiple: bool = False
    multiple_separator: str = " "

    def validate_target(self, target: str) -> bool:
        """Validate a target against all configured rules."""
        for rule in self.rules:
            valid = rule.validate_target(target, multiple=self.multiple)
            if valid is True:
                return True
            continue
        raise InputValidationError(error="No matched validation rules", target=target)

    @property
    def field_type(self) -> t.Literal["text", "select", None]:
        """Get the linked field type."""

        if self.field.is_select:
            return "select"
        if self.field.is_text or self.field.is_ip:
            return "text"
        return None

    @field_validator("plugins")
    def validate_plugins(cls: "Directive", plugins: t.List[str]) -> t.List[str]:
        """Validate and register configured plugins."""
        plugin_dir = Settings.app_path / "plugins"

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

    def frontend(self: "Directive") -> t.Dict[str, t.Any]:
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
                value["info"] = md.read()

        if self.field.is_select:
            value["options"] = [o.export_dict() for o in self.field.options if o is not None]

        return value


class BuiltinDirective(Directive, unique_by=("id", "table_output", "platforms")):
    """Natively-supported directive."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: Series[str] = []


DirectiveT = t.Union[BuiltinDirective, Directive]


class Directives(MultiModel[Directive], model=Directive, unique_by="id"):
    """Collection of directives."""

    def device_builtins(self, *, platform: str, table_output: bool):
        """Get builtin directives for a device."""

        return Directives(
            *(
                self.table_if_available(directive) if table_output else directive  # noqa: IF100 GFY
                for directive in self
                if directive._hyperglass_builtin is True
                and platform in getattr(directive, "platforms", ())
            )
        )

    def table_if_available(self, directive: "Directive") -> "Directive":
        """Get the table-output variant of a directive if it exists."""
        for _directive in self:
            if _directive.id == directive.table_output:
                return _directive
        return directive

    @classmethod
    def new(cls, /, *raw_directives: t.Dict[str, t.Any]) -> "Directives":
        """Create a new Directives collection from raw directive configurations."""
        directives = (
            Directive(id=name, **directive)
            for raw_directive in raw_directives
            for name, directive in raw_directive.items()
        )
        return Directives(*directives)
