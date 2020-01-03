"""Validate branding configuration variables."""

from typing import Optional

# Third Party Imports
from pydantic import StrictStr, StrictInt, StrictBool
from pydantic import constr
from pydantic import validator
from pydantic.color import Color

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Branding(HyperglassModel):
    """Validation model for params.branding."""

    site_title: StrictStr = "hyperglass"

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

    class Logo(HyperglassModel):
        """Validation model for params.branding.logo."""

        logo_path: StrictStr = "ui/images/hyperglass-dark.png"
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

        class Config:
            """Override pydantic config."""

            fields = {"logo_path": "path"}

    class PeeringDb(HyperglassModel):
        """Validation model for params.branding.peering_db."""

        enable: StrictBool = True

    class Terms(HyperglassModel):
        """Validation model for params.branding.terms."""

        enable: StrictBool = True

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
        bgp_route: StrictStr = "BGP Route"
        bgp_community: StrictStr = "BGP Community"
        bgp_aspath: StrictStr = "BGP AS Path"
        ping: StrictStr = "Ping"
        traceroute: StrictStr = "Traceroute"

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
    font: Font = Font()
    help_menu: HelpMenu = HelpMenu()
    logo: Logo = Logo()
    peering_db: PeeringDb = PeeringDb()
    terms: Terms = Terms()
    text: Text = Text()
