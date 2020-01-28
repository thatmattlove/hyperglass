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


class Web(HyperglassModel):
    """Validation model for params.branding."""

    class Colors(HyperglassModel):
        """Validation model for params.colors."""

        primary: Color = "#40798c"
        secondary: Color = "#330036"
        danger: Color = "#a21024"
        warning: Color = "#eec643"
        light: Color = "#fbfffe"
        dark: Color = "#383541"
        background: Color = "#fbfffe"

        def dict(self, *args, **kwargs):
            """Return dict for colors only."""
            _dict = {}
            for k, v in self.__dict__.items():
                _dict.update({k: v.as_hex()})
            return _dict

    class Credit(HyperglassModel):
        """Validation model for params.branding.credit."""

        enable: StrictBool = True

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
        """Validation model for params.branding.help_menu."""

        enable: StrictBool = True
        file: Optional[FilePath]
        title: StrictStr = "Help"

    class Logo(HyperglassModel):
        """Validation model for params.branding.logo."""

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
                Path(__file__).parent.parent.parent
                / "static/images/hyperglass-light.png"
            )
            default_logo_dark = (
                Path(__file__).parent.parent.parent
                / "static/images/hyperglass-dark.png"
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

    class ExternalLink(HyperglassModel):
        """Validation model for params.branding.external_link."""

        enable: StrictBool = True
        title: StrictStr = "PeeringDB"
        url: HttpUrl = "https://www.peeringdb.com/AS{primary_asn}"

    class Terms(HyperglassModel):
        """Validation model for params.branding.terms."""

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
        terms: StrictStr = "Terms"
        info: StrictStr = "Help"
        peeringdb = "PeeringDB"
        fqdn_tooltip: StrictStr = "Use {protocol}"
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

    colors: Colors = Colors()
    credit: Credit = Credit()
    external_link: ExternalLink = ExternalLink()
    font: Font = Font()
    help_menu: HelpMenu = HelpMenu()
    logo: Logo = Logo()
    opengraph: OpenGraph = OpenGraph()
    terms: Terms = Terms()
    text: Text = Text()
