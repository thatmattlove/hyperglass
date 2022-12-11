"""UI Configuration models."""

# Standard Library
from typing import Any, Dict, List, Tuple, Union, Literal, Optional

# Third Party
from pydantic import StrictStr, StrictBool

# Local
from .main import HyperglassModel
from .config.web import WebPublic
from .config.cache import CachePublic
from .config.params import ParamsPublic
from .config.messages import Messages

Alignment = Union[Literal["left"], Literal["center"], Literal["right"], None]
StructuredDataField = Tuple[str, str, Alignment]


class UIDirective(HyperglassModel):
    """UI: Directive."""

    id: StrictStr
    name: StrictStr
    field_type: StrictStr
    groups: List[StrictStr]
    description: StrictStr
    info: Optional[str] = None
    options: Optional[List[Dict[str, Any]]]


class UILocation(HyperglassModel):
    """UI: Location (Device)."""

    id: StrictStr
    name: StrictStr
    group: Optional[StrictStr]
    avatar: Optional[StrictStr]
    description: Optional[StrictStr]
    directives: List[UIDirective] = []


class UIDevices(HyperglassModel):
    """UI: Devices."""

    group: Optional[StrictStr]
    locations: List[UILocation] = []


class UIContent(HyperglassModel):
    """UI: Content."""

    credit: StrictStr
    greeting: StrictStr


class UIParameters(ParamsPublic, HyperglassModel):
    """UI Configuration Parameters."""

    cache: CachePublic
    web: WebPublic
    messages: Messages
    version: StrictStr
    devices: List[UIDevices] = []
    parsed_data_fields: Tuple[StructuredDataField, ...]
    content: UIContent
    developer_mode: StrictBool
