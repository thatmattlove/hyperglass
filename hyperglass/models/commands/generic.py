import json
from ipaddress import IPv4Network, IPv6Network
from typing import Optional, Sequence, Union, Dict
from typing_extensions import Literal
from pydantic import StrictStr, PrivateAttr, conint, validator, FilePath
from ..main import HyperglassModel
from ..config.params import Params
from hyperglass.configuration.markdown import get_markdown

IPv4PrefixLength = conint(ge=0, le=32)
IPv6PrefixLength = conint(ge=0, le=128)


class Policy(HyperglassModel):
    network: Union[IPv4Network, IPv6Network]
    action: Literal["permit", "deny"]

    @validator("ge", check_fields=False)
    def validate_ge(cls, value: int, values: Dict) -> int:
        """Ensure ge is at least the size of the input prefix."""

        network_len = values["network"].prefixlen

        if network_len > value:
            value = network_len

        return value


class Policy4(Policy):
    ge: IPv4PrefixLength = 0
    le: IPv4PrefixLength = 32


class Policy6(Policy):
    ge: IPv6PrefixLength = 0
    le: IPv6PrefixLength = 128


class Input(HyperglassModel):
    _type: PrivateAttr
    description: StrictStr

    def is_select(self) -> bool:
        return self._type == "select"

    def is_text(self) -> bool:
        return self._type == "text"

    def is_ip(self) -> bool:
        return self._type == "ip"


class Text(Input):
    _type: PrivateAttr = "text"
    validation: Optional[StrictStr]


class IPInput(Input):
    _type: PrivateAttr = "ip"
    validation: Union[Policy4, Policy6]


class Option(HyperglassModel):
    name: Optional[StrictStr]
    value: StrictStr


class Select(Input):
    _type: PrivateAttr = "select"
    options: Sequence[Option]


class Directive(HyperglassModel):
    id: StrictStr
    name: StrictStr
    command: Union[StrictStr, Sequence[StrictStr]]
    field: Union[Text, Select, IPInput, None]
    info: Optional[FilePath]
    attrs: Dict = {}
    groups: Sequence[
        StrictStr
    ] = []  # TODO: Flesh this out. Replace VRFs, but use same logic in React to filter available commands for multi-device queries.

    @validator("command")
    def validate_command(cls, value: Union[str, Sequence[str]]) -> Sequence[str]:
        if isinstance(value, str):
            return [value]
        return value

    def get_commands(self, target: str) -> Sequence[str]:
        return [s.format(target=target, **self.attrs) for s in self.command]

    @property
    def field_type(self) -> Literal["text", "select", None]:
        if self.field.is_select():
            return "select"
        elif self.field.is_text() or self.field.is_ip():
            return "text"
        return None

    def frontend(self, params: Params) -> Dict:

        value = {
            "name": self.name,
            "field_type": self.field_type,
            "groups": self.groups,
            "description": self.field.description,
            "info": None,
        }

        if self.info is not None:
            content_params = json.loads(
                params.json(
                    include={
                        "primary_asn",
                        "org_name",
                        "site_title",
                        "site_description",
                    }
                )
            )
            with self.info.open() as md:
                value["info"] = {
                    "enable": True,
                    "params": content_params,
                    "content": md.read(),
                }

        if self.field_type == "select":
            value["options"]: [o.export_dict() for o in self.field.options]

        return value
