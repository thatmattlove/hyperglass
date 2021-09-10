"""UI Configuration models."""

# Standard Library
from typing import Any, Dict, List, Tuple, Union, Literal, Optional

# Third Party
from pydantic import StrictStr, StrictBool

# Local
from .main import HyperglassUIModel, as_ui_model
from .config.web import WebPublic
from .config.cache import CachePublic
from .config.params import ParamsPublic
from .config.messages import Messages

Alignment = Union[Literal["left"], Literal["center"], Literal["right"], None]
StructuredDataField = Tuple[str, str, Alignment]

CacheUI = as_ui_model("CacheUI", CachePublic)
WebUI = as_ui_model("WebUI", WebPublic)
MessagesUI = as_ui_model("MessagesUI", Messages)


class UIDirectiveInfo(HyperglassUIModel):
    """UI: Directive Info."""

    enable: StrictBool
    params: Dict[str, str]
    content: StrictStr


class UIDirective(HyperglassUIModel):
    """UI: Directive."""

    id: StrictStr
    name: StrictStr
    field_type: StrictStr
    groups: List[StrictStr]
    description: StrictStr
    info: Optional[UIDirectiveInfo] = None
    options: Optional[List[Dict[str, Any]]]


class UILocation(HyperglassUIModel):
    """UI: Location (Device)."""

    id: StrictStr
    name: StrictStr
    network: StrictStr
    directives: List[UIDirective] = []


class UINetwork(HyperglassUIModel):
    """UI: Network."""

    display_name: StrictStr
    locations: List[UILocation] = []


class UIContent(HyperglassUIModel):
    """UI: Content."""

    credit: StrictStr
    greeting: StrictStr


class UIParameters(HyperglassUIModel, ParamsPublic):
    """UI Configuration Parameters."""

    cache: CacheUI
    web: WebUI
    messages: MessagesUI
    version: StrictStr
    networks: List[UINetwork] = []
    parsed_data_fields: Tuple[StructuredDataField, ...]
    content: UIContent
