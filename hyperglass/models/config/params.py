"""Configuration validation entry point."""

# Standard Library
from typing import Any, Dict, List, Tuple, Union, Literal
from pathlib import Path

# Third Party
from pydantic import Field, StrictInt, StrictStr, StrictBool, validator

# Project
from hyperglass.settings import Settings

# Local
from .web import Web
from .docs import Docs
from ..main import HyperglassModel
from .cache import Cache
from .logging import Logging
from .messages import Messages
from .structured import Structured

Localhost = Literal["localhost"]


class ParamsPublic(HyperglassModel):
    """Public configuration parameters."""

    request_timeout: StrictInt = Field(
        90,
        title="Request Timeout",
        description="Global timeout in seconds for all requests. The frontend application (UI) uses this field's exact value when submitting queries. The backend application uses this field's value, minus one second, for its own timeout handling. This is to ensure a contextual timeout error is presented to the end user in the event of a backend application timeout.",
    )
    primary_asn: Union[StrictInt, StrictStr] = Field(
        "65001",
        title="Primary ASN",
        description="Your network's primary ASN. This field is used to set some useful defaults such as the subtitle and PeeringDB URL.",
    )
    org_name: StrictStr = Field(
        "Beloved Hyperglass User",
        title="Organization Name",
        description="Your organization's name. This field is used in the UI & API documentation to set fields such as `<meta/>` HTML tags for SEO and the terms & conditions footer component.",
    )
    site_title: StrictStr = Field(
        "hyperglass",
        title="Site Title",
        description="The name of your hyperglass site. This field is used in the UI & API documentation to set fields such as the `<title/>` HTML tag, and the terms & conditions footer component.",
    )
    site_description: StrictStr = Field(
        "{org_name} Network Looking Glass",
        title="Site Description",
        description='A short description of your hyperglass site. This field is used in th UI & API documentation to set the `<meta name="description"/>` tag. `{org_name}` may be used to insert the value of the `org_name` field.',
    )


class Params(ParamsPublic, HyperglassModel):
    """Validation model for all configuration variables."""

    # Top Level Params

    fake_output: StrictBool = Field(
        False,
        title="Fake Output",
        description="If enabled, the hyperglass backend will return static fake output for development/testing purposes.",
    )
    cors_origins: List[StrictStr] = Field(
        [],
        title="Cross-Origin Resource Sharing",
        description="Allowed CORS hosts. By default, no CORS hosts are allowed.",
    )
    plugins: List[StrictStr] = []

    # Sub Level Params
    cache: Cache = Cache()
    docs: Docs = Docs()
    logging: Logging = Logging()
    messages: Messages = Messages()
    structured: Structured = Structured()
    web: Web = Web()

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 1}

    def __init__(self, **kw: Any) -> None:
        return super().__init__(**self.convert_paths(kw))

    @validator("site_description")
    def validate_site_description(cls: "Params", value: str, values: Dict[str, Any]) -> str:
        """Format the site descripion with the org_name field."""
        return value.format(org_name=values["org_name"])

    @validator("primary_asn")
    def validate_primary_asn(cls: "Params", value: Union[int, str]) -> str:
        """Stringify primary_asn if passed as an integer."""
        return str(value)

    @validator("plugins")
    def validate_plugins(cls: "Params", value: List[str]) -> List[str]:
        """Validate and register configured plugins."""
        plugin_dir = Settings.app_path / "plugins"

        if plugin_dir.exists():
            # Path objects whose file names match configured file names, should work
            # whether or not file extension is specified.
            matching_plugins = (
                f
                for f in plugin_dir.iterdir()
                if f.name.split(".")[0] in (p.split(".")[0] for p in value)
            )
            return [str(f) for f in matching_plugins]
        return []

    def common_plugins(self) -> Tuple[Path, ...]:
        """Get all validated external common plugins as Path objects."""
        return tuple(Path(p) for p in self.plugins)

    def frontend(self) -> Dict[str, Any]:
        """Export UI-specific parameters."""

        return self.export_dict(
            include={
                "cache": {"show_text", "timeout"},
                "developer_mode": ...,
                "primary_asn": ...,
                "request_timeout": ...,
                "org_name": ...,
                "site_title": ...,
                "site_description": ...,
                "web": ...,
                "messages": ...,
            }
        )
