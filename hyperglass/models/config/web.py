"""Validate branding configuration variables."""

# Standard Library
import typing as t
from pathlib import Path

# Third Party
from pydantic import (
    HttpUrl,
    FilePath,
    StrictInt,
    StrictStr,
    StrictBool,
    constr,
    validator,
    root_validator,
)
from pydantic.color import Color

# Project
from hyperglass.defaults import DEFAULT_HELP, DEFAULT_TERMS
from hyperglass.constants import DNS_OVER_HTTPS, FUNC_COLOR_MAP

# Local
from ..main import HyperglassModel
from .opengraph import OpenGraph

DEFAULT_IMAGES = Path(__file__).parent.parent.parent / "images"

Percentage = constr(regex=r"^([1-9][0-9]?|100)\%$")
TitleMode = constr(regex=("logo_only|text_only|logo_title|logo_subtitle|all"))
ColorMode = constr(regex=r"light|dark")
DOHProvider = constr(regex="|".join(DNS_OVER_HTTPS.keys()))
Title = constr(max_length=32)
Side = constr(regex=r"left|right")
LocationDisplayMode = t.Literal["auto", "dropdown", "gallery"]


class Credit(HyperglassModel):
    """Validation model for developer credit."""

    enable: StrictBool = True


class Link(HyperglassModel):
    """Validation model for generic link."""

    title: StrictStr
    url: HttpUrl
    show_icon: StrictBool = True
    side: Side = "left"
    order: StrictInt = 0


class Menu(HyperglassModel):
    """Validation model for generic menu."""

    title: StrictStr
    content: StrictStr
    side: Side = "left"
    order: StrictInt = 0

    @validator("content")
    def validate_content(cls: "Menu", value: str) -> str:
        """Read content from file if a path is provided."""

        if len(value) < 260:
            path = Path(value)
            if path.exists():
                with path.open("r") as f:
                    return f.read()
            else:
                return value
        return value


class Greeting(HyperglassModel):
    """Validation model for greeting modal."""

    enable: StrictBool = False
    file: t.Optional[FilePath]
    title: StrictStr = "Welcome"
    button: StrictStr = "Continue"
    required: StrictBool = False

    @validator("file")
    def validate_file(cls, value, values):
        """Ensure file is specified if greeting is enabled."""
        if values["enable"] and value is None:
            raise ValueError("Greeting is enabled, but no file is specified.")
        return value


class Logo(HyperglassModel):
    """Validation model for logo configuration."""

    light: FilePath = DEFAULT_IMAGES / "hyperglass-light.svg"
    dark: FilePath = DEFAULT_IMAGES / "hyperglass-dark.svg"
    favicon: FilePath = DEFAULT_IMAGES / "hyperglass-icon.svg"
    width: t.Optional[t.Union[StrictInt, Percentage]] = "100%"
    height: t.Optional[t.Union[StrictInt, Percentage]]


class LogoPublic(Logo):
    """Public logo configuration."""

    light_format: StrictStr
    dark_format: StrictStr


class Text(HyperglassModel):
    """Validation model for params.branding.text."""

    title_mode: TitleMode = "logo_only"
    title: Title = "hyperglass"
    subtitle: Title = "Network Looking Glass"
    query_location: StrictStr = "Location"
    query_type: StrictStr = "Query Type"
    query_target: StrictStr = "Target"
    fqdn_tooltip: StrictStr = "Use {protocol}"  # Formatted by Javascript
    fqdn_message: StrictStr = "Your browser has resolved {fqdn} to"  # Formatted by Javascript
    fqdn_error: StrictStr = "Unable to resolve {fqdn}"  # Formatted by Javascript
    fqdn_error_button: StrictStr = "Try Again"
    cache_prefix: StrictStr = "Results cached for "
    cache_icon: StrictStr = "Cached from {time} UTC"  # Formatted by Javascript
    complete_time: StrictStr = "Completed in {seconds}"  # Formatted by Javascript
    rpki_invalid: StrictStr = "Invalid"
    rpki_valid: StrictStr = "Valid"
    rpki_unknown: StrictStr = "No ROAs Exist"
    rpki_unverified: StrictStr = "Not Verified"
    no_communities: StrictStr = "No Communities"
    ip_error: StrictStr = "Unable to determine IP Address"
    no_ip: StrictStr = "No {protocol} Address"
    ip_select: StrictStr = "Select an IP Address"
    ip_button: StrictStr = "My IP"

    @validator("title_mode")
    def validate_title_mode(cls: "Text", value: str) -> str:
        """Set legacy logo_title to logo_subtitle."""
        if value == "logo_title":
            value = "logo_subtitle"
        return value

    @validator("cache_prefix")
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
    primary: t.Optional[Color]
    secondary: t.Optional[Color]
    success: t.Optional[Color]
    warning: t.Optional[Color]
    error: t.Optional[Color]
    danger: t.Optional[Color]

    @validator(*FUNC_COLOR_MAP.keys(), pre=True, always=True)
    def validate_colors(
        cls: "ThemeColors", value: str, values: t.Dict[str, t.Optional[str]], field
    ) -> str:
        """Set default functional color mapping."""
        if value is None:
            default_color = FUNC_COLOR_MAP[field.name]
            value = str(values[default_color])
        return value

    def dict(self, *args: t.Any, **kwargs: t.Any) -> t.Dict[str, str]:
        """Return dict for colors only."""
        return {k: v.as_hex() for k, v in self.__dict__.items()}


class ThemeFonts(HyperglassModel):
    """Validation model for theme fonts."""

    body: StrictStr = "Nunito"
    mono: StrictStr = "Fira Code"


class Theme(HyperglassModel):
    """Validation model for theme variables."""

    colors: ThemeColors = ThemeColors()
    default_color_mode: t.Optional[ColorMode]
    fonts: ThemeFonts = ThemeFonts()


class DnsOverHttps(HyperglassModel):
    """Validation model for DNS over HTTPS resolution."""

    name: DOHProvider = "cloudflare"
    url: StrictStr = ""

    @root_validator
    def validate_dns(cls: "DnsOverHttps", values: t.Dict[str, str]) -> t.Dict[str, str]:
        """Assign url field to model based on selected provider."""
        provider = values["name"]
        values["url"] = DNS_OVER_HTTPS[provider]
        return values


class HighlightPattern(HyperglassModel):
    """Validation model for highlight pattern configuration."""

    pattern: StrictStr
    label: t.Optional[StrictStr] = None
    color: StrictStr = "primary"

    @validator("color")
    def validate_color(cls: "HighlightPattern", value: str) -> str:
        """Ensure highlight color is a valid theme color."""
        colors = list(ThemeColors.__fields__.keys())
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
    custom_javascript: t.Optional[FilePath]
    custom_html: t.Optional[FilePath]
    highlight: t.List[HighlightPattern] = []


class WebPublic(Web):
    """Public web configuration."""

    logo: LogoPublic
