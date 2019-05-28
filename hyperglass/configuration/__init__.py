# Module Imports
import os
import math
import toml

# Project Imports
import hyperglass

# Project Directories
dir = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)
# TOML Imports
configuration = toml.load(os.path.join(dir, "configuration.toml"))
devices = toml.load(os.path.join(dir, "devices.toml"))


def blacklist():
    b = toml.load(os.path.join(dir, "blacklist.toml"))
    return b["blacklist"]


def requires_ipv6_cidr(nos):
    r = toml.load(os.path.join(dir, "requires_ipv6_cidr.toml"))
    nos_list = r["requires_ipv6_cidr"]
    if nos in nos_list:
        return True
    else:
        return False


def networks():
    """Returns dictionary of ASNs as keys, list of associated locations as values.
    Used for populating the /routers/<asn> Flask route."""
    asn_dict = {}
    rl = devices["router"]
    for r in rl.values():
        asn = r["asn"]
        if asn in asn_dict:
            asn_dict[asn].append(r["location"])
        else:
            asn_dict[asn] = [r["location"]]
    return asn_dict


def networks_list():
    networks_dict = {}
    rl = devices["router"]
    for r in rl.values():
        asn = r["asn"]
        if asn in networks_dict:
            networks_dict[asn].append(
                dict(
                    location=r["location"],
                    hostname=r["name"],
                    display_name=r["display_name"],
                    requires_ipv6_cidr=requires_ipv6_cidr(r["type"]),
                )
            )
        else:
            networks_dict[asn] = [
                dict(
                    location=r["location"],
                    hostname=r["name"],
                    display_name=r["display_name"],
                    requires_ipv6_cidr=requires_ipv6_cidr(r["type"]),
                )
            ]
    return networks_dict


class codes:
    """Class for easy calling & recalling of http success/error codes"""

    def __init__(self):
        # 200 OK: renders standard display text
        self.success = 200
        # 405 Method Not Allowed: Renders Bulma "warning" class notification message with message text
        self.warning = 405
        # 415 Unsupported Media Type: Renders Bulma "danger" class notification message with message text
        self.danger = 415


class command:
    def __init__(self, nos):
        c = toml.load(os.path.join(dir, "commands.toml"))
        self.dual = c[nos][0]["dual"]
        self.ipv4 = c[nos][0]["ipv4"]
        self.ipv6 = c[nos][0]["ipv6"]

    def __call__(self):
        return vars(self)


class credential:
    def __init__(self, cred):
        c_list = devices["credential"]
        self.username = c_list[cred]["username"]
        self.password = c_list[cred]["password"]

    def __call__(self):
        return vars(self)


class device:
    """Class to define & export all device variables"""

    def __init__(self, device):
        d = devices["router"][device]
        self.address = d.get("address")
        self.asn = d.get("asn")
        self.src_addr_ipv4 = d.get("src_addr_ipv4")
        self.src_addr_ipv6 = d.get("src_addr_ipv6")
        self.credential = d.get("credential")
        self.location = d.get("location")
        self.name = d.get("name")
        self.display_name = d.get("display_name")
        self.port = d.get("port")
        self.type = d.get("type")
        self.proxy = d.get("proxy")

    def __call__(self):
        return vars(self)


class proxy:
    def __init__(self, proxy):
        p = devices["proxy"][proxy]
        self.address = p["address"]
        self.username = p["username"]
        self.password = p["password"]
        self.type = p["type"]
        self.ssh_command = p["ssh_command"]


class general:
    """Class to define and export config variables and export default values if undefined"""

    def __init__(self):
        g = configuration["general"][0]
        self.primary_asn = g.get("primary_asn", "65000")
        self.org_name = g.get("org_name", "The Company")
        self.debug = g.get("debug", False)
        self.google_analytics = g.get("google_analytics", "")
        self.msg_error_querytype = g.get(
            "msg_error_querytype", "You must select a query type."
        )
        self.msg_error_notallowed = g.get(
            "msg_error_notallowed", "<b>{i}</b> is not allowed."
        )
        self.msg_error_ipv6cidr = g.get(
            "msg_error_ipv6cidr",
            "<b>{d}</b> requires IPv6 BGP lookups to be in CIDR notation.",
        )
        self.msg_error_invalidip = g.get(
            "msg_error_invalidip", "<b>{i}</b> is not a valid IP address."
        )
        self.msg_error_invaliddual = g.get(
            "msg_error_invaliddual", "<b>{i}</b> is an invalid {qt}."
        )
        self.msg_error_general = g.get("msg_error_general", "A general error occurred.")
        self.msg_max_prefix = g.get(
            "msg_max_prefix",
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific.",
        )
        self.rate_limit_query = g.get("rate_limit_query", "5")
        self.message_rate_limit_query = g.get(
            "message_rate_limit_query",
            f"Query limit of {self.rate_limit_query} per minute reached. Please wait one minute and try again.",
        )
        self.enable_bgp_route = g.get("enable_bgp_route", True)
        self.enable_bgp_community = g.get("enable_bgp_community", True)
        self.enable_bgp_aspath = g.get("enable_bgp_aspath", True)
        self.enable_ping = g.get("enable_ping", True)
        self.enable_traceroute = g.get("enable_traceroute", True)
        self.rate_limit_site = g.get("rate_limit_site", "120")
        self.cache_timeout = g.get("cache_timeout", 120)
        self.cache_directory = g.get(
            "cache_directory", os.path.join(hyperglass_root, ".flask_cache")
        )
        self.enable_max_prefix = g.get("enable_max_prefix", False)
        self.max_prefix_length_ipv4 = g.get("max_prefix_length_ipv4", 24)
        self.max_prefix_length_ipv6 = g.get("max_prefix_length_ipv6", 64)


class branding:
    """Class to define and export branding variables and export default values if undefined"""

    def __init__(self):
        b = configuration["branding"][0]
        self.site_title = b.get("site_title", "hyperglass")
        self.title = b.get("title", "hyperglass")
        self.subtitle = b.get("subtitle", f"AS{general().primary_asn}")
        self.title_mode = b.get("title_mode", "logo_only")
        self.enable_footer = b.get("enable_footer", True)
        self.enable_credit = b.get("enable_credit", True)
        self.color_btn_submit = b.get("color_btn_submit", "#40798c")

        self.color_tag_loctitle = b.get("color_tag_loctitle", "#330036")
        self.color_tag_cmdtitle = b.get("color_tag_cmdtitle", "#330036")
        self.color_tag_cmd = b.get("color_tag_cmd", "#ff5e5b")
        self.color_tag_loc = b.get("color_tag_loc", "#40798c")
        self.color_progressbar = b.get("color_progressbar", "#40798c")
        self.color_bg = b.get("color_bg", "#fbfffe")
        self.color_danger = b.get("color_danger", "#ff3860")
        self.logo_path = b.get(
            "logo_path",
            os.path.join(hyperglass_root, "static/images/hyperglass-dark.png"),
        )
        self.logo_width = b.get("logo_width", "384")
        self.favicon_dir = b.get("favicon_path", "static/images/favicon/")
        self.placeholder_prefix = b.get(
            "placeholder_prefix", "IP, Prefix, Community, or AS_PATH"
        )
        self.show_peeringdb = b.get("show_peeringdb", True)
        self.text_results = b.get("text_results", "Results")
        self.text_location = b.get("text_location", "Select Location...")
        self.text_cache = b.get(
            "text_cache",
            f"Results will be cached for {math.ceil(general().cache_timeout / 60)} minutes.",
        )
        self.primary_font_name = b.get("primary_font_name", "Nunito")
        self.primary_font_url = b.get(
            "primary_font_url",
            "https://fonts.googleapis.com/css?family=Nunito:400,600,700",
        )
        self.mono_font_name = b.get("mono_font_name", "Fira Mono")
        self.mono_font_url = b.get(
            "mono_font_url", "https://fonts.googleapis.com/css?family=Fira+Mono"
        )
        self.text_limiter_title = b.get("text_limiter_title", "Limit Reached")
        self.text_limiter_subtitle = b.get(
            "text_limiter_subtitle",
            f"You have accessed this site more than {general().rate_limit_site} times in the last minute.",
        )
        self.text_500_title = b.get("text_500_title", "Error")
        self.text_500_subtitle = b.get("text_500_subtitle", "Something went wrong.")
        self.text_500_button = b.get("text_500_button", "Home")
        self.text_help_bgp_route = b.get(
            "text_help_bgp_route",
            "Performs BGP table lookup based on IPv4/IPv6 prefix.",
        )
        self.text_help_bgp_community = b.get(
            "text_help_bgp_community",
            'Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195">Large</a> community value.',
        )
        self.text_help_bgp_aspath = b.get(
            "text_help_bgp_aspath",
            'Performs BGP table lookup based on <code>AS_PATH</code> regular expression.<br>For commonly used BGP regular expressions, <a href="https://hyperglass.readthedocs.io/en/latest/Extras/common_as_path_regex/">click here</a>.',
        )
        self.text_help_ping = b.get(
            "text_help_ping", "Sends 5 ICMP echo requests to the target."
        )
        self.text_help_traceroute = b.get(
            "text_help_traceroute",
            'Performs UDP Based traceroute to the target.<br>For information about how to interpret traceroute results, <a href="https://www.nanog.org/meetings/nanog45/presentations/Sunday/RAS_traceroute_N45.pdf">click here</a>.',
        )
