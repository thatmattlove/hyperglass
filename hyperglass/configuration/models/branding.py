"""Validate branding configuration variables."""

# Third Party Imports
from pydantic import constr
from pydantic import validator
from pydantic.color import Color

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Branding(HyperglassModel):
    """Validation model for params.branding."""

    site_title: str = "hyperglass"

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

        enable: bool = True

    class Font(HyperglassModel):
        """Validation model for params.branding.font."""

        primary: str = "Nunito"
        mono: str = "Fira Code"

    class HelpMenu(HyperglassModel):
        """Validation model for params.branding.help_menu."""

        enable: bool = True

    class Logo(HyperglassModel):
        """Validation model for params.branding.logo."""

        logo_path: str = "ui/images/hyperglass-dark.png"
        width: int = 384
        favicons: str = "ui/images/favicons/"

        @validator("favicons")
        def favicons_trailing_slash(cls, value):  # noqa: N805
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

        enable: bool = True

    class Terms(HyperglassModel):
        """Validation model for params.branding.terms."""

        enable: bool = True

    class Text(HyperglassModel):
        """Validation model for params.branding.text."""

        title_mode: constr(regex=("logo_only|text_only|logo_title|all")) = "logo_only"
        title: str = "hyperglass"
        subtitle: str = "AS{primary_asn}"
        query_location: str = "Location"
        query_type: str = "Query Type"
        query_target: str = "Target"
        query_vrf: str = "Routing Table"
        terms: str = "Terms"
        info: str = "Help"
        peeringdb = "PeeringDB"
        bgp_route: str = "BGP Route"
        bgp_community: str = "BGP Community"
        bgp_aspath: str = "BGP AS Path"
        ping: str = "Ping"
        traceroute: str = "Traceroute"

        class Error404(HyperglassModel):
            """Validation model for 404 Error Page."""

            title: str = "Error"
            subtitle: str = "{uri} isn't a thing"
            button: str = "Home"

        class Error500(HyperglassModel):
            """Validation model for 500 Error Page."""

            title: str = "Error"
            subtitle: str = "Something Went Wrong"
            button: str = "Home"

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
