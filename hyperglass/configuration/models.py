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
    # asn: int
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

    # @staticmethod
    # def build_network_lists(valid_devices):
    #     """
    #     Builds locations dict, which is converted to JSON and passed to
    #     JavaScript to associate locations with the selected network/ASN.

    #     Builds networks dict, which is used to render the network/ASN
    #     select element contents.
    #     """
    #     locations_dict = {}
    #     networks_dict = {}
    #     for (dev, params) in valid_devices.items():
    #         asn = str(params["asn"])
    #         if asn in locations_dict:
    #             locations_dict[asn].append(
    #                 {
    #                     "location": params["location"],
    #                     "hostname": dev,
    #                     "display_name": params["display_name"],
    #                 }
    #             )
    #             networks_dict[asn].append(params["location"])
    #         elif asn not in locations_dict:
    #             locations_dict[asn] = [
    #                 {
    #                     "location": params["location"],
    #                     "hostname": dev,
    #                     "display_name": params["display_name"],
    #                 }
    #             ]
    #             networks_dict[asn] = [params["location"]]
    #     if not locations_dict:
    #         raise ConfigError('Unable to build locations list from "devices.yaml"')
    #     if not networks_dict:
    #         raise ConfigError('Unable to build networks list from "devices.yaml"')
    #     return (locations_dict, networks_dict)
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
        # locations_dict, networks_dict = Routers.build_network_lists(routers)
        Routers.routers = routers
        Routers.hostnames = hostnames
        # Routers.locations = locations_dict
        # Routers.networks = networks_dict
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


class Branding(BaseSettings):
    """Class model for params.branding"""

    site_name: str = "hyperglass"

    class Colors(BaseSettings):
        """Class model for params.colors"""

        background: Color = "#fbfffe"
        button_submit: Color = "#40798c"
        danger: Color = "#ff3860"
        progress_bar: Color = "#40798c"

        class Tag(BaseSettings):
            """Class model for params.colors.tag"""

            query_type: Color = "#ff5e5b"
            query_type_title: Color = "#330036"
            location: Color = "#40798c"
            location_title: Color = "#330036"

        tag: Tag = Tag()

    class Credit(BaseSettings):
        """Class model for params.branding.credit"""

        enable: bool = True

    class Font(BaseSettings):
        """Class model for params.branding.font"""

        class Primary(BaseSettings):
            """Class model for params.branding.font.primary"""

            name: str = "Nunito"
            url: UrlStr = "https://fonts.googleapis.com/css?family=Nunito:400,600,700"

        class Mono(BaseSettings):
            """Class model for params.branding.font.mono"""

            name: str = "Fira Mono"
            url: UrlStr = "https://fonts.googleapis.com/css?family=Fira+Mono"

        primary: Primary = Primary()
        mono: Mono = Mono()

    class Footer(BaseSettings):
        """Class model for params.branding.font"""

        enable: bool = True

    class Logo(BaseSettings):
        """Class model for params.branding.logo"""

        path: str = "static/images/hyperglass-dark.png"
        width: int = 384
        favicons: str = "static/images/favicons/"

    class PeeringDb(BaseSettings):
        """Class model for params.branding.peering_db"""

        enable: bool = True

    credit: Credit = Credit()
    font: Font = Font()
    footer: Footer = Footer()
    logo: Logo = Logo()
    colors: Colors = Colors()
    peering_db: PeeringDb = PeeringDb()

    class Text(BaseSettings):
        """Class model for params.branding.text"""

        query_type: str = "Query Type"
        title_mode: str = "logo_only"
        title: str = "hyperglass"
        subtitle: str = "AS{primary_asn}".format(primary_asn=General().primary_asn)
        results: str = "Results"
        location: str = "Select Location..."
        query_placeholder: str = "IP, Prefix, Community, or AS Path"
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

    credit: Credit = Credit()
    footer: Footer = Footer()
    text: Text = Text()


class Messages(BaseSettings):
    """Class model for params.messages"""

    no_query_type: str = "Query Type must be specified."
    no_location: str = "A location must be selected."
    no_input: str = "A target must be specified"
    not_allowed: str = "<b>{i}</b> is not allowed."
    requires_ipv6_cidr: str = (
        "<b>{d}</b> requires IPv6 BGP lookups" "to be in CIDR notation."
    )
    invalid_ip: str = "<b>{i}</b> is not a valid IP address."
    invalid_dual: str = "<b>{i}</b> is an invalid {qt}."
    general: str = "An error occurred."
    directed_cidr: str = "<b>{q}</b> queries can not be in CIDR format."


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
