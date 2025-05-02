"""Configuration validation entry point."""

# Standard Library
import typing as t
import urllib.parse
from pathlib import Path

# Third Party
from pydantic import Field, HttpUrl, ConfigDict, ValidationInfo, field_validator

# Project
from hyperglass.settings import Settings
from hyperglass.constants import __version__

# Local
from .web import Web
from .docs import Docs
from ..main import HyperglassModel
from .cache import Cache
from .logging import Logging
from .messages import Messages
from .structured import Structured

Localhost = t.Literal["localhost"]


class APIParams(t.TypedDict):
    """/api/info response model."""

    name: str
    organization: str
    primary_asn: int
    version: str


class ParamsPublic(HyperglassModel):
    """Public configuration parameters."""

    request_timeout: int = Field(
        90,
        title="Request Timeout",
        description="Global timeout in seconds for all requests. The frontend application (UI) uses this field's exact value when submitting queries. The backend application uses this field's value, minus one second, for its own timeout handling. This is to ensure a contextual timeout error is presented to the end user in the event of a backend application timeout.",
    )
    primary_asn: t.Union[int, str] = Field(
        "65001",
        title="Primary ASN",
        description="Your network's primary ASN. This field is used to set some useful defaults such as the subtitle and PeeringDB URL.",
    )
    org_name: str = Field(
        "Beloved Hyperglass User",
        title="Organization Name",
        description="Your organization's name. This field is used in the UI & API documentation to set fields such as `<meta/>` HTML tags for SEO and the terms & conditions footer component.",
    )
    site_title: str = Field(
        "hyperglass",
        title="Site Title",
        description="The name of your hyperglass site. This field is used in the UI & API documentation to set fields such as the `<title/>` HTML tag, and the terms & conditions footer component.",
    )
    site_description: str = Field(
        "{org_name} Network Looking Glass",
        title="Site Description",
        description='A short description of your hyperglass site. This field is used in th UI & API documentation to set the `<meta name="description"/>` tag. `{org_name}` may be used to insert the value of the `org_name` field.',
    )


class Params(ParamsPublic, HyperglassModel):
    """Validation model for all configuration variables."""

    model_config = ConfigDict(json_schema_extra={"level": 1})

    # Top Level Params

    fake_output: bool = Field(
        False,
        title="Fake Output",
        description="If enabled, the hyperglass backend will return static fake output for development/testing purposes.",
    )
    cors_origins: t.List[str] = Field(
        [],
        title="Cross-Origin Resource Sharing",
        description="Allowed CORS hosts. By default, no CORS hosts are allowed.",
    )
    plugins: t.List[str] = []

    # Sub Level Params
    cache: Cache = Cache()
    docs: Docs = Docs()
    logging: Logging = Logging()
    messages: Messages = Messages()
    structured: Structured = Structured()
    web: Web = Web()

    def __init__(self, **kw: t.Any) -> None:
        return super().__init__(**self.convert_paths(kw))

    @field_validator("site_description")
    def validate_site_description(cls: "Params", value: str, info: ValidationInfo) -> str:
        """Format the site description with the org_name field."""
        return value.format(org_name=info.data.get("org_name"))

    @field_validator("primary_asn")
    def validate_primary_asn(cls: "Params", value: t.Union[int, str]) -> str:
        """Stringify primary_asn if passed as an integer."""
        return str(value)

    @field_validator("plugins")
    def validate_plugins(cls: "Params", value: t.List[str]) -> t.List[str]:
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

    @field_validator("web", mode="after")
    @classmethod
    def validate_web(cls, web: Web, info: ValidationInfo) -> Web:
        """String-format Link URLs."""
        for link in web.links:
            url = urllib.parse.unquote(str(link.url), encoding="utf-8", errors="replace").format(
                primary_asn=info.data.get("primary_asn", "65000")
            )
            link.url = HttpUrl(url)

        for menu in web.menus:
            menu.content = menu.content.format(
                site_title=info.data.get("site_title", "hyperglass"),
                org_name=info.data.get("org_name", "hyperglass"),
                version=__version__,
            )
        return web

    def common_plugins(self) -> t.Tuple[Path, ...]:
        """Get all validated external common plugins as Path objects."""
        return tuple(Path(p) for p in self.plugins)

    def export_api(self) -> APIParams:
        """Export API-specific parameters."""
        return {
            "name": self.site_title,
            "organization": self.org_name,
            "primary_asn": int(self.primary_asn),
            "version": __version__,
        }

    def frontend(self) -> t.Dict[str, t.Any]:
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
