"""Validate branding configuration variables."""

# Standard Library Imports
from pathlib import Path
from typing import Optional

# Third Party Imports
from pydantic import FilePath
from pydantic import HttpUrl
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import constr
from pydantic import root_validator
from pydantic import validator
from pydantic.color import Color

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models.opengraph import OpenGraph
from hyperglass.constants import DNS_OVER_HTTPS
from hyperglass.constants import FUNC_COLOR_MAP


class Analytics(HyperglassModel):
    """Validation model for Google Analytics."""

    enable: StrictBool = False
    id: Optional[StrictStr]

    @validator("id")
    def validate_id(cls, value, values):
        """Ensure ID is set if analytics is enabled.

        Arguments:
            value {str|None} -- Google Analytics ID
            values {[type]} -- Already-validated model parameters

        Raises:
            ValueError: Raised if analytics is enabled but no ID is set.

        Returns:
            {str|None} -- Google Analytics ID if enabled.
        """
        if values["enable"] and value is None:
            raise ValueError("Analytics is enabled, but no ID is set.")
        return value


class Credit(HyperglassModel):
    """Validation model for developer credit."""

    enable: StrictBool = True


class ExternalLink(HyperglassModel):
    """Validation model for external link."""

    enable: StrictBool = True
    title: StrictStr = "PeeringDB"
    url: HttpUrl = "https://www.peeringdb.com/AS{primary_asn}"


class Font(HyperglassModel):
    """Validation model for params.branding.font."""

    class Primary(HyperglassModel):
        """Validation model for params.branding.font.primary."""

        name: StrictStr = "Nunito"
        size: StrictStr = "1rem"

    class Mono(HyperglassModel):
        """Validation model for params.branding.font.mono."""

        name: StrictStr = "Fira Code"
        size: StrictStr = "87.5%"

    primary: Primary = Primary()
    mono: Mono = Mono()


class HelpMenu(HyperglassModel):
    """Validation model for generic help menu."""

    enable: StrictBool = True
    file: Optional[FilePath]
    title: StrictStr = "Help"


class Logo(HyperglassModel):
    """Validation model for logo configuration."""

    light: Optional[FilePath]
    dark: Optional[FilePath]
    width: StrictInt = 384
    height: Optional[StrictInt]
    favicons: StrictStr = "ui/images/favicons/"

    @validator("favicons")
    def favicons_trailing_slash(cls, value):
        """If the favicons path does not end in a '/', append it."""
        chars = list(value)
        if chars[len(chars) - 1] != "/":
            chars.append("/")
        return "".join(chars)

    @root_validator(pre=True)
    def validate_logo_model(cls, values):
        """Set default opengraph image location.

        Arguments:
            values {dict} -- Unvalidated model

        Returns:
            {dict} -- Modified model
        """
        logo_light = values.get("light")
        logo_dark = values.get("dark")
        default_logo_light = (
            Path(__file__).parent.parent.parent / "static/images/hyperglass-light.png"
        )
        default_logo_dark = (
            Path(__file__).parent.parent.parent / "static/images/hyperglass-dark.png"
        )

        # Use light logo as dark logo if dark logo is undefined.
        if logo_light is not None and logo_dark is None:
            values["dark"] = logo_light

        # Use dark logo as light logo if light logo is undefined.
        if logo_dark is not None and logo_light is None:
            values["light"] = logo_dark

        # Set default logo paths if logo is undefined.
        if logo_light is None and logo_dark is None:
            values["light"] = default_logo_light
            values["dark"] = default_logo_dark

        return values

    @validator("light", "dark")
    def validate_logos(cls, value):
        """Convert file path to URL path.

        Arguments:
            value {FilePath} -- Path to logo file.

        Returns:
            {str} -- Formatted logo path
        """
        return "".join(str(value).split("static")[1::])

    class Config:
        """Override pydantic config."""

        fields = {"logo_path": "path"}


class Terms(HyperglassModel):
    """Validation model for terms & conditions."""

    enable: StrictBool = True
    file: Optional[FilePath]
    title: StrictStr = "Terms"


class Text(HyperglassModel):
    """Validation model for params.branding.text."""

    title_mode: constr(regex=("logo_only|text_only|logo_title|all")) = "logo_only"
    title: StrictStr = "hyperglass"
    subtitle: StrictStr = "AS{primary_asn}"
    query_location: StrictStr = "Location"
    query_type: StrictStr = "Query Type"
    query_target: StrictStr = "Target"
    query_vrf: StrictStr = "Routing Table"
    fqdn_tooltip: StrictStr = "Use {protocol}"  # Formatted by Javascript
    cache: StrictStr = "Results will be cached for {timeout} {period}."

    class Error404(HyperglassModel):
        """Validation model for 404 Error Page."""

        title: StrictStr = "Error"
        subtitle: StrictStr = "{uri} isn't a thing"
        button: StrictStr = "Home"

    class Error500(HyperglassModel):
        """Validation model for 500 Error Page."""

        title: StrictStr = "Error"
        subtitle: StrictStr = "Something Went Wrong"
        button: StrictStr = "Home"

    error404: Error404 = Error404()
    error500: Error500 = Error500()


class Theme(HyperglassModel):
    """Validation model for theme variables."""

    class Colors(HyperglassModel):
        """Validation model for theme colors."""

        black: Color = "#262626"
        white: Color = "#f7f7f7"
        gray: Color = "#c1c7cc"
        red: Color = "#d84b4b"
        orange: Color = "ff6b35"
        yellow: Color = "#edae49"
        green: Color = "#35b246"
        blue: Color = "#314cb6"
        teal: Color = "#35b299"
        cyan: Color = "#118ab2"
        pink: Color = "#f2607d"
        purple: Color = "#8d30b5"
        primary: Optional[Color]
        secondary: Optional[Color]
        success: Optional[Color]
        warning: Optional[Color]
        error: Optional[Color]
        danger: Optional[Color]

        @validator(*FUNC_COLOR_MAP.keys(), pre=True, always=True)
        def validate_colors(cls, value, values, field):
            """Set default functional color mapping.

            Arguments:
                value {str|None} -- Functional color
                values {str} -- Already-validated colors

            Returns:
                {str} -- Mapped color.
            """

            if value is None:
                default_color = FUNC_COLOR_MAP[field.name]
                value = str(values[default_color])
            return value

        def dict(self, *args, **kwargs):
            """Return dict for colors only."""
            return {k: v.as_hex() for k, v in self.__dict__.items()}

    class Fonts(HyperglassModel):
        """Validation model for theme fonts."""

        body: StrictStr = "Nunito"
        mono: StrictStr = "Fira Code"

    colors: Colors = Colors()
    fonts: Fonts = Fonts()


class DnsOverHttps(HyperglassModel):
    """Validation model for DNS over HTTPS resolution."""

    name: constr(regex="|".join(DNS_OVER_HTTPS.keys())) = "cloudflare"

    @root_validator
    def validate_dns(cls, values):
        """Assign url field to model based on selected provider.

        Arguments:
            values {dict} -- Dict of selected provider

        Returns:
            {dict} -- Dict with url attribute
        """
        provider = values["name"]
        values["url"] = DNS_OVER_HTTPS[provider]
        return values


class Web(HyperglassModel):
    """Validation model for all web/browser-related configuration."""

    credit: Credit = Credit()
    dns_provider: DnsOverHttps = DnsOverHttps()
    external_link: ExternalLink = ExternalLink()
    font: Font = Font()
    help_menu: HelpMenu = HelpMenu()
    logo: Logo = Logo()
    opengraph: OpenGraph = OpenGraph()
    terms: Terms = Terms()
    text: Text = Text()
    theme: Theme = Theme()
