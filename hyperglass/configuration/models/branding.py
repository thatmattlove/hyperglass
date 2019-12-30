"""Validate branding configuration variables."""

# Third Party Imports
from pydantic import constr
from pydantic import validator
from pydantic.color import Color

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class Branding(HyperglassModel):
    """Class model for params.branding"""

    site_title: str = "hyperglass"

    class Colors(HyperglassModel):
        """Class model for params.colors"""

        primary: Color = "#40798c"
        secondary: Color = "#330036"
        danger: Color = "#a21024"
        warning: Color = "#eec643"
        light: Color = "#fbfffe"
        dark: Color = "#383541"
        background: Color = "#fbfffe"

        def dict(self, *args, **kwargs):
            _dict = {}
            for k, v in self.__dict__.items():
                _dict.update({k: v.as_hex()})
            return _dict

    class Credit(HyperglassModel):
        """Class model for params.branding.credit"""

        enable: bool = True

    class Font(HyperglassModel):
        """Class model for params.branding.font"""

        primary: str = "Nunito"
        mono: str = "Fira Code"

    class HelpMenu(HyperglassModel):
        """Class model for params.branding.help_menu"""

        enable: bool = True

    class Logo(HyperglassModel):
        """Class model for params.branding.logo"""

        path: str = "ui/images/hyperglass-dark.png"
        width: int = 384
        favicons: str = "ui/images/favicons/"

        @validator("favicons")
        def favicons_trailing_slash(cls, value):
            """
            If the favicons path does not end in a '/', append it.
            """
            chars = [char for char in value]
            if chars[len(chars) - 1] != "/":
                chars.append("/")
            return "".join(chars)

    class PeeringDb(HyperglassModel):
        """Class model for params.branding.peering_db"""

        enable: bool = True

    class Terms(HyperglassModel):
        """Class model for params.branding.terms"""

        enable: bool = True

    class Text(HyperglassModel):
        """Class model for params.branding.text"""

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
            """Class model for 404 Error Page"""

            title: str = "Error"
            subtitle: str = "{uri} isn't a thing"
            button: str = "Home"

        class Error500(HyperglassModel):
            """Class model for 500 Error Page"""

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
