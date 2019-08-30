"""
Defines models for all config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
import re
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from math import ceil
from typing import List
from typing import Union

# Third Party Imports
from pydantic import BaseSettings
from pydantic import IPvAnyAddress
from pydantic import IPvAnyNetwork
from pydantic import SecretStr
from pydantic import UrlStr
from pydantic import constr
from pydantic import validator
from pydantic.color import Color

# Project Imports
from hyperglass.constants import Supported
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import UnsupportedDevice


def clean_name(_name):
    """
    Converts any "desirable" seperators to underscore, then
    removes all characters that are unsupported in Python class
    variable names. Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


class Router(BaseSettings):
    """Model for per-router config in devices.yaml."""

    address: Union[IPvAnyAddress, str]
    network: str
    src_addr_ipv4: IPv4Address
    src_addr_ipv6: IPv6Address
    credential: str
    location: str
    display_name: str
    port: int
    nos: str
    proxy: Union[str, None] = None

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """Validates that passed nos string is supported by hyperglass"""
        if not Supported.is_supported(v):
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v

    @validator("credential", "proxy", "location")
    def clean_credential(cls, v):  # noqa: N805
        """Remove or replace unsupported characters from field values"""
        return clean_name(v)


class Routers(BaseSettings):
    """Base model for devices class."""

    @staticmethod
    def build_network_lists(valid_devices):
        """
        Builds locations dict, which is converted to JSON and passed to
        JavaScript to associate locations with the selected network/ASN.

        Builds networks dict, which is used to render the network/ASN
        select element contents.
        """

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the Routers class.
        """
        routers = {}
        hostnames = []
        for (devname, params) in input_params.items():
            dev = clean_name(devname)
            router_params = Router(**params)
            setattr(Routers, dev, router_params)
            routers.update({dev: router_params.dict()})
            hostnames.append(dev)
        Routers.routers = routers
        Routers.hostnames = hostnames
        return Routers()

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True


class Network(BaseSettings):
    """Model for per-network/asn config in devices.yaml"""

    display_name: str


class Networks(BaseSettings):
    """Base model for networks class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the credentials class.
        """
        obj = Networks()
        networks = {}
        for (netname, params) in input_params.items():
            netname = clean_name(netname)
            setattr(Networks, netname, Network(**params))
            networks.update({netname: Network(**params).dict()})
        Networks.networks = networks
        return obj

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True


class Credential(BaseSettings):
    """Model for per-credential config in devices.yaml"""

    username: str
    password: SecretStr


class Credentials(BaseSettings):
    """Base model for credentials class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the credentials class.
        """
        obj = Credentials()
        for (credname, params) in input_params.items():
            cred = clean_name(credname)
            setattr(Credentials, cred, Credential(**params))
        return obj

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True


class Proxy(BaseSettings):
    """Model for per-proxy config in devices.yaml"""

    address: Union[IPvAnyAddress, str]
    port: int = 22
    username: str
    password: SecretStr
    nos: str
    ssh_command: str

    @validator("nos")
    def supported_nos(cls, v):  # noqa: N805
        """Validates that passed nos string is supported by hyperglass"""
        if not v == "linux_ssh":
            raise UnsupportedDevice(f'"{v}" device type is not supported.')
        return v


class Proxies(BaseSettings):
    """Base model for proxies class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, removes unsupported
        characters from device names, dynamically sets attributes for
        the proxies class.
        """
        obj = Proxies()
        for (devname, params) in input_params.items():
            dev = clean_name(devname)
            setattr(Proxies, dev, Proxy(**params))
        return obj

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True


class General(BaseSettings):
    """Class model for params.general"""

    debug: bool = False
    primary_asn: str = "65001"
    org_name: str = "The Company"
    google_analytics: Union[str, None] = None
    redis_host: Union[str, IPvAnyNetwork] = "localhost"
    redis_port: int = 6379
    requires_ipv6_cidr: List[str] = ["cisco_ios", "cisco_nxos"]
    query_timeout: int = 15


class Branding(BaseSettings):
    """Class model for params.branding"""

    site_name: str = "hyperglass"

    class Colors(BaseSettings):
        """Class model for params.colors"""

        primary: Color = "#40798c"
        secondary: Color = "#330036"
        danger: Color = "#ff5e5b"
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
        subtitle: str = "AS{primary_asn}".format(primary_asn=General().primary_asn)
        location: str = "Location"
        query_type: str = "Query"
        query_placeholder: str = "Target"
        terms: str = "Terms"
        info: str = "Help"
        peeringdb = "PeeringDB"
        bgp_route: str = "BGP Route"
        bgp_community: str = "BGP Community"
        bgp_aspath: str = "BGP AS Path"
        ping: str = "Ping"
        traceroute: str = "Traceroute"

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

            message: str = "Unable to reach <b>{target}</b>"

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


class Messages(BaseSettings):
    """Class model for params.messages"""

    no_query_type: str = "Query Type must be specified."
    no_location: str = "A location must be selected."
    no_input: str = "A target must be specified"
    blacklist: str = "{target} is not allowed."
    max_prefix: str = "{target} prefix-length must be shorter than {max_length}."
    requires_ipv6_cidr: str = (
        "{location} requires IPv6 BGP lookups to be in CIDR notation."
    )
    invalid_input: str = "{target} is not a valid {query_type}."
    general: str = "Something went wrong."
    directed_cidr: str = "{query_type} queries can not be in CIDR format."
    request_timeout: str = "Request timed out."


class Features(BaseSettings):
    """Class model for params.features"""

    class BgpRoute(BaseSettings):
        """Class model for params.features.bgp_route"""

        enable: bool = True

    class BgpCommunity(BaseSettings):
        """Class model for params.features.bgp_community"""

        enable: bool = True

        class Regex(BaseSettings):
            """Class model for params.features.bgp_community.regex"""

            decimal: str = r"^[0-9]{1,10}$"
            extended_as: str = r"^([0-9]{0,5})\:([0-9]{1,5})$"
            large: str = r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"

        regex: Regex = Regex()

    class BgpAsPath(BaseSettings):
        """Class model for params.features.bgp_aspath"""

        enable: bool = True

        class Regex(BaseSettings):
            """Class model for params.bgp_aspath.regex"""

            mode: constr(regex="asplain|asdot") = "asplain"
            asplain: str = r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"
            asdot: str = (
                r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"
            )

        regex: Regex = Regex()

    class Ping(BaseSettings):
        """Class model for params.features.ping"""

        enable: bool = True

    class Traceroute(BaseSettings):
        """Class model for params.features.traceroute"""

        enable: bool = True

    class Blacklist(BaseSettings):
        """Class model for params.features.blacklist"""

        enable: bool = True
        networks: List[IPvAnyNetwork] = [
            "198.18.0.0/15",
            "100.64.0.0/10",
            "2001:db8::/32",
            "10.0.0.0/8",
            "192.168.0.0/16",
            "172.16.0.0/12",
        ]

    class Cache(BaseSettings):
        """Class model for params.features.cache"""

        redis_id: int = 0
        timeout: int = 120
        show_text: bool = True
        text: str = "Results will be cached for {timeout} minutes.".format(
            timeout=ceil(timeout / 60)
        )

    class MaxPrefix(BaseSettings):
        """Class model for params.features.max_prefix"""

        enable: bool = False
        ipv4: int = 24
        ipv6: int = 64
        message: str = (
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific."
        )

    class RateLimit(BaseSettings):
        """Class model for params.features.rate_limit"""

        redis_id: int = 1

        class Query(BaseSettings):
            """Class model for params.features.rate_limit.query"""

            rate: int = 5
            period: str = "minute"
            title: str = "Query Limit Reached"
            message: str = (
                "Query limit of {rate} per {period} reached. "
                "Please wait one minute and try again."
            ).format(rate=rate, period=period)
            button: str = "Try Again"

        class Site(BaseSettings):
            """Class model for params.features.rate_limit.site"""

            rate: int = 60
            period: str = "minute"
            title: str = "Limit Reached"
            subtitle: str = (
                "You have accessed this site more than {rate} "
                "times in the last {period}."
            ).format(rate=rate, period=period)
            button: str = "Try Again"

        query: Query = Query()
        site: Site = Site()

    bgp_route: BgpRoute = BgpRoute()
    bgp_community: BgpCommunity = BgpCommunity()
    bgp_aspath: BgpAsPath = BgpAsPath()
    ping: Ping = Ping()
    traceroute: Traceroute = Traceroute()
    blacklist: Blacklist = Blacklist()
    cache: Cache = Cache()
    max_prefix: MaxPrefix = MaxPrefix()
    rate_limit: RateLimit = RateLimit()


class Params(BaseSettings):
    """Base model for params"""

    general: General = General()
    features: Features = Features()
    branding: Branding = Branding()
    messages: Messages = Messages()

    class Config:
        """Pydantic Config"""

        validate_all = True
        validate_assignment = True


class NosModel(BaseSettings):
    """Class model for non-default commands"""

    class Dual(BaseSettings):
        """Class model for non-default dual afi commands"""

        bgp_aspath: str = None
        bgp_community: str = None

    class IPv4(BaseSettings):
        """Class model for non-default ipv4 commands"""

        bgp_route: str = None
        ping: str = None
        traceroute: str = None

    class IPv6(BaseSettings):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = None
        ping: str = None
        traceroute: str = None

    dual: Dual = Dual()
    ipv4: IPv4 = IPv4()
    ipv6: IPv6 = IPv6()


class Commands(BaseSettings):
    """Base class for commands class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, dynamically sets
        attributes for the commands class.
        """
        obj = Commands()
        for (nos, cmds) in input_params.items():
            setattr(Commands, nos, NosModel(**cmds))
        return obj

    class CiscoIOS(BaseSettings):
        """Class model for default cisco_ios commands"""

        class Dual(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community = "show bgp all community {target}"
            bgp_aspath = 'show bgp all quote-regexp "{target}"'

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_route = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
            ping = "ping {target} repeat 5 source {source}"
            traceroute = "traceroute {target} timeout 1 probe 2 source {source}"

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_route = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
            ping = "ping ipv6 {target} repeat 5 source {source}"
            traceroute = "traceroute ipv6 {target} timeout 1 probe 2 source {source}"

        dual: Dual = Dual()
        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()

    class CiscoXR(BaseSettings):
        """Class model for default cisco_xr commands"""

        class Dual(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community = (
                "show bgp all unicast community {target} | utility egrep -v "
                '"\\(BGP |Table |Non-stop\\)"'
            )
            bgp_aspath = (
                "show bgp all unicast regexp {target} | utility egrep -v "
                '"\\(BGP |Table |Non-stop\\)"'
            )

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_route = (
                "show bgp ipv4 unicast {target} | util egrep \\(BGP routing table "
                "entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            )
            ping = "ping ipv4 {target} count 5 source {src_addr_ipv4}"
            traceroute = "traceroute ipv4 {target} timeout 1 probe 2 source {source}"

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_route = (
                "show bgp ipv6 unicast {target} | util egrep \\(BGP routing table "
                "entry|Path \\#|aggregated by|Origin |Community:|validity| from \\)"
            )
            ping = "ping ipv6 {target} count 5 source {src_addr_ipv6}"
            traceroute = "traceroute ipv6 {target} timeout 1 probe 2 source {source}"

        dual: Dual = Dual()
        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()

    class Juniper(BaseSettings):
        """Class model for default juniper commands"""

        class Dual(BaseSettings):
            """Default commands for dual afi commands"""

            bgp_community = "show route protocol bgp community {target}"
            bgp_aspath = "show route protocol bgp aspath-regex {target}"

        class IPv4(BaseSettings):
            """Default commands for ipv4 commands"""

            bgp_route = "show route protocol bgp table inet.0 {target} detail"
            ping = "ping inet {target} count 5 source {src_addr_ipv4}"
            traceroute = "traceroute inet {target} wait 1 source {source}"

        class IPv6(BaseSettings):
            """Default commands for ipv6 commands"""

            bgp_route = "show route protocol bgp table inet6.0 {target} detail"
            ping = "ping inet6 {target} count 5 source {src_addr_ipv6}"
            traceroute = "traceroute inet6 {target} wait 1 source {source}"

        dual: Dual = Dual()
        ipv4: IPv4 = IPv4()
        ipv6: IPv6 = IPv6()

    cisco_ios: NosModel = CiscoIOS()
    cisco_xr: NosModel = CiscoXR()
    juniper: NosModel = Juniper()

    class Config:
        """Pydantic Config"""

        validate_all = False
        validate_assignment = True
