"""Validate branding configuration variables."""

# Standard Library
import typing as t
from pathlib import Path

# Third Party
from pydantic import Field, HttpUrl, FilePath, ValidationInfo, field_validator, model_validator
from pydantic_extra_types.color import Color

# Project
from hyperglass.defaults import DEFAULT_HELP, DEFAULT_TERMS
from hyperglass.constants import DNS_OVER_HTTPS, FUNC_COLOR_MAP

# Local
from ..main import HyperglassModel
from .opengraph import OpenGraph

DEFAULT_IMAGES = Path(__file__).parent.parent.parent / "images"
DOH_PROVIDERS_PATTERN = "|".join(DNS_OVER_HTTPS.keys())
PERCENTAGE_PATTERN = r"^([1-9][0-9]?|100)\%?$"

Percentage = Field(pattern=r"^([1-9][0-9]?|100)\%$")
TitleMode = t.Literal["logo_only", "text_only", "logo_subtitle", "all"]
ColorMode = t.Literal["light", "dark"]
Side = t.Literal["left", "right"]
LocationDisplayMode = t.Literal["auto", "dropdown", "gallery"]


class Credit(HyperglassModel):
    """Validation model for developer credit."""

    enable: bool = True


class Link(HyperglassModel):
    """Validation model for generic link."""

    title: str
    url: HttpUrl
    show_icon: bool = True
    side: Side = "left"
    order: int = 0


class Menu(HyperglassModel):
    """Validation model for generic menu."""

    title: str
    content: str
    side: Side = "left"
    order: int = 0

    @field_validator("content")
    def validate_content(cls: "Menu", value: str) -> str:
        """Read content from file if a path is provided."""

        if len(value) < 260:
            path = Path(value)
            if path.is_file() and path.exists():
                with path.open("r") as f:
                    return f.read()
        return value


class Greeting(HyperglassModel):
    """Validation model for greeting modal."""

    enable: bool = False
    file: t.Optional[FilePath] = None
    title: str = "Welcome"
    button: str = "Continue"
    required: bool = False

    @field_validator("file")
    def validate_file(cls, value: str, info: ValidationInfo):
        """Ensure file is specified if greeting is enabled."""
        if info.data.get("enable") and value is None:
            raise ValueError("Greeting is enabled, but no file is specified.")
        return value


class Logo(HyperglassModel):
    """Validation model for logo configuration."""

    light: FilePath = DEFAULT_IMAGES / "hyperglass-light.svg"
    dark: FilePath = DEFAULT_IMAGES / "hyperglass-dark.svg"
    favicon: FilePath = DEFAULT_IMAGES / "hyperglass-icon.svg"
    width: str = Field(default="50%", pattern=PERCENTAGE_PATTERN)
    height: t.Optional[str] = Field(default=None, pattern=PERCENTAGE_PATTERN)


class LogoPublic(Logo):
    """Public logo configuration."""

    light_format: str
    dark_format: str


class Text(HyperglassModel):
    """Validation model for params.branding.text."""

    title_mode: TitleMode = "logo_only"
    title: str = Field(default="hyperglass", max_length=32)
    subtitle: str = Field(default="Network Looking Glass", max_length=32)
    query_location: str = "Location"
    query_type: str = "Query Type"
    query_target: str = "Target"
    fqdn_tooltip: str = "Use {protocol}"  # Formatted by Javascript
    fqdn_message: str = "Your browser has resolved {fqdn} to"  # Formatted by Javascript
    fqdn_error: str = "Unable to resolve {fqdn}"  # Formatted by Javascript
    fqdn_error_button: str = "Try Again"
    cache_prefix: str = "Results cached for "
    cache_icon: str = "Cached from {time} UTC"  # Formatted by Javascript
    complete_time: str = "Completed in {seconds}"  # Formatted by Javascript
    rpki_invalid: str = "Invalid"
    rpki_valid: str = "Valid"
    rpki_unknown: str = "No ROAs Exist"
    rpki_unverified: str = "Not Verified"
    no_communities: str = "No Communities"
    ip_error: str = "Unable to determine IP Address"
    no_ip: str = "No {protocol} Address"
    ip_select: str = "Select an IP Address"
    ip_button: str = "My IP"

    @field_validator("cache_prefix")
    def validate_cache_prefix(cls: "Text", value: str) -> str:
        """Ensure trailing whitespace."""
        return " ".join(value.split()) + " "


class ThemeColors(HyperglassModel):
    """Validation model for theme colors."""

    black: Color = "#000000"
    white: Color = "#ffffff"
    dark: Color = "#010101"
    light: Color = "#f5f6f7"
    gray: Color = "#c1c7cc"
    red: Color = "#d84b4b"
    orange: Color = "#ff6b35"
    yellow: Color = "#edae49"
    green: Color = "#35b246"
    blue: Color = "#314cb6"
    teal: Color = "#35b299"
    cyan: Color = "#118ab2"
    pink: Color = "#f2607d"
    purple: Color = "#8d30b5"
    primary: t.Optional[Color] = None
    secondary: t.Optional[Color] = None
    success: t.Optional[Color] = None
    warning: t.Optional[Color] = None
    error: t.Optional[Color] = None
    danger: t.Optional[Color] = None

    @field_validator(*FUNC_COLOR_MAP.keys(), mode="before")
    def validate_colors(cls: "ThemeColors", value: str, info: ValidationInfo) -> str:
        """Set default functional color mapping."""
        if value is None:
            default_color = FUNC_COLOR_MAP[info.field_name]
            value = str(info.data[default_color])
        return value

    def dict(self, *args: t.Any, **kwargs: t.Any) -> t.Dict[str, str]:
        """Return dict for colors only."""
        return {k: v.as_hex() for k, v in self.__dict__.items()}


class ThemeFonts(HyperglassModel):
    """Validation model for theme fonts."""

    body: str = "Nunito"
    mono: str = "Fira Code"


class Theme(HyperglassModel):
    """Validation model for theme variables."""

    colors: ThemeColors = ThemeColors()
    default_color_mode: t.Optional[ColorMode] = None
    fonts: ThemeFonts = ThemeFonts()


class DnsOverHttps(HyperglassModel):
    """Validation model for DNS over HTTPS resolution."""

    name: str = "cloudflare"
    url: str = ""

    @model_validator(mode="before")
    def validate_dns(cls, data: "DnsOverHttps") -> t.Dict[str, str]:
        """Assign url field to model based on selected provider."""
        name = data.get("name", "cloudflare")
        url = data.get("url", DNS_OVER_HTTPS["cloudflare"])
        if url not in DNS_OVER_HTTPS.values():
            return {
                "name": "custom",
                "url": url,
            }
        url = DNS_OVER_HTTPS[name]
        return {
            "name": name,
            "url": url,
        }


class HighlightPattern(HyperglassModel):
    """Validation model for highlight pattern configuration."""

    pattern: str
    label: t.Optional[str] = None
    color: str = "primary"

    @field_validator("color")
    def validate_color(cls: "HighlightPattern", value: str) -> str:
        """Ensure highlight color is a valid theme color."""
        colors = list(ThemeColors.model_fields.keys())
        color_list = "\n  - ".join(("", *colors))
        if value not in colors:
            raise ValueError(
                "{!r} is not a supported color. Must be one of:{!s}".format(value, color_list)
            )
        return value


class Web(HyperglassModel):
    """Validation model for all web/browser-related configuration."""

    credit: Credit = Credit()
    dns_provider: DnsOverHttps = DnsOverHttps()
    links: t.Sequence[Link] = [
        Link(title="PeeringDB", url="https://www.peeringdb.com/asn/{primary_asn}")
    ]
    menus: t.Sequence[Menu] = [
        Menu(title="Terms", content=DEFAULT_TERMS),
        Menu(title="Help", content=DEFAULT_HELP),
    ]
    greeting: Greeting = Greeting()
    logo: Logo = Logo()
    opengraph: OpenGraph = OpenGraph()
    text: Text = Text()
    theme: Theme = Theme()
    location_display_mode: LocationDisplayMode = "auto"
    custom_javascript: t.Optional[FilePath] = None
    custom_html: t.Optional[FilePath] = None
    highlight: t.List[HighlightPattern] = []


class WebPublic(Web):
    """Public web configuration."""

    logo: LogoPublic
