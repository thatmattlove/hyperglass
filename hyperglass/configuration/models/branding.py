"""
Defines models for all Branding variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""

# Third Party Imports
from pydantic import BaseSettings
from pydantic import validator
from pydantic.color import Color


class Branding(BaseSettings):
    """Class model for params.branding"""

    site_name: str = "hyperglass"

    class Colors(BaseSettings):
        """Class model for params.colors"""

        primary: Color = "#40798c"
        secondary: Color = "#330036"
        danger: Color = "#a21024"
        warning: Color = "#eec643"
        light: Color = "#fbfffe"
        dark: Color = "#383541"
        background: Color = "#fbfffe"

    class Credit(BaseSettings):
        """Class model for params.branding.credit"""

        enable: bool = True

    class Font(BaseSettings):
        """Class model for params.branding.font"""

        primary: str = "Nunito"
        mono: str = "Fira Code"

    class HelpMenu(BaseSettings):
        """Class model for params.branding.help_menu"""

        enable: bool = True

    class Logo(BaseSettings):
        """Class model for params.branding.logo"""

        path: str = "ui/images/hyperglass-dark.png"
        width: int = 384
        favicons: str = "ui/images/favicons/"

    class PeeringDb(BaseSettings):
        """Class model for params.branding.peering_db"""

        enable: bool = True

    class Terms(BaseSettings):
        """Class model for params.branding.terms"""

        enable: bool = True

    class Text(BaseSettings):
        """Class model for params.branding.text"""

        title_mode: str = "logo_only"
        title: str = "hyperglass"
        subtitle: str = "AS{primary_asn}"
        query_location: str = "Location"
        query_type: str = "Query"
        query_target: str = "Target"
        terms: str = "Terms"
        info: str = "Help"
        peeringdb = "PeeringDB"
        bgp_route: str = "BGP Route"
        bgp_community: str = "BGP Community"
        bgp_aspath: str = "BGP AS Path"
        ping: str = "Ping"
        traceroute: str = "Traceroute"
        vrf: str = "VRF"

        class Error404(BaseSettings):
            """Class model for 404 Error Page"""

            title: str = "Error"
            subtitle: str = "{uri} isn't a thing"
            button: str = "Home"

        class Error500(BaseSettings):
            """Class model for 500 Error Page"""

            title: str = "Error"
            subtitle: str = "Something Went Wrong"
            button: str = "Home"

        class Error504(BaseSettings):
            """Class model for 504 Error Element"""

            message: str = "Unable to reach {target}"

        error404: Error404 = Error404()
        error500: Error500 = Error500()
        error504: Error504 = Error504()

        @validator("title_mode")
        def check_title_mode(cls, v):
            """Verifies title_mode matches supported values"""
            supported_modes = ["logo_only", "text_only", "logo_title", "all"]
            if v not in supported_modes:
                raise ValueError("title_mode must be one of {}".format(supported_modes))
            return v

    colors: Colors = Colors()
    credit: Credit = Credit()
    font: Font = Font()
    help_menu: HelpMenu = HelpMenu()
    logo: Logo = Logo()
    peering_db: PeeringDb = PeeringDb()
    terms: Terms = Terms()
    text: Text = Text()
