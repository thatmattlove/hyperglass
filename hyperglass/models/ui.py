"""UI Configuration models."""

# Standard Library
import typing as t

# Local
from .main import HyperglassModel
from .config.web import WebPublic
from .config.cache import Cache
from .config.params import ParamsPublic
from .config.messages import Messages

Alignment = t.Union[t.Literal["left"], t.Literal["center"], t.Literal["right"], None]
StructuredDataField = t.Tuple[str, str, Alignment]


class UIDirective(HyperglassModel):
    """UI: Directive."""

    id: str
    name: str
    field_type: str
    groups: t.List[str]
    description: str
    info: t.Optional[str] = None
    options: t.Optional[t.List[t.Dict[str, t.Any]]] = None


class UILocation(HyperglassModel):
    """UI: Location (Device)."""

    id: str
    name: str
    group: t.Optional[str] = None
    avatar: t.Optional[str] = None
    description: t.Optional[str] = None
    directives: t.List[UIDirective] = []


class UIDevices(HyperglassModel):
    """UI: Devices."""

    group: t.Optional[str] = None
    locations: t.List[UILocation] = []


class UIContent(HyperglassModel):
    """UI: Content."""

    credit: str
    greeting: str


class UIParameters(ParamsPublic, HyperglassModel):
    """UI Configuration Parameters."""

    cache: Cache
    web: WebPublic
    messages: Messages
    version: str
    devices: t.List[UIDevices] = []
    parsed_data_fields: t.Tuple[StructuredDataField, ...]
    content: UIContent
    developer_mode: bool
