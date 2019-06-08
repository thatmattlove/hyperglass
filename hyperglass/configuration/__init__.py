# https://github.com/checktheroads/hyperglass
"""
Imports configuration varibles from configuration files and returns default values if undefined.
"""
# Standard Imports
import os
import math

# Module Imports
import toml

# Project Imports
import hyperglass

# Project Directories
working_dir = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)

# TOML Imports
configuration = toml.load(os.path.join(working_dir, "configuration.toml"))
devices = toml.load(os.path.join(working_dir, "devices.toml"))


def blacklist():
    """Returns list of subnets/IPs defined in blacklist.toml"""
    blacklist_config = toml.load(os.path.join(working_dir, "blacklist.toml"))
    return blacklist_config["blacklist"]


def requires_ipv6_cidr(nos):
    """Returns boolean for input NOS association with the NOS list defined in \
    requires_ipv6_cidr.toml"""
    nos_list = configuration["requires_ipv6_cidr"]
    return bool(nos in nos_list)


def networks():
    """Returns dictionary of ASNs as keys, list of associated locations as values. Imported as a \
    Jinja2 variable on the main page that populates the network/ASN select class."""
    asn_dict = {}
    routers_list = devices["router"]
    for router_config in routers_list.values():
        asn = router_config["asn"]
        if asn in asn_dict:
            asn_dict[asn].append(router_config["location"])
        else:
            asn_dict[asn] = [router_config["location"]]
    return asn_dict


def networks_list():
    """Returns a dictionary of ASNs as keys, list of associated locations, router hostnames, and \
    router display names as keys. Used by Flask to populate the /routers/<asn> route, which is \
    ingested by a JS Ajax call to populate the list of locations associated with the selected \
    network/ASN on the main page."""
    networks_dict = {}
    routers_list = devices["router"]
    for router_config in routers_list.values():
        asn = router_config["asn"]
        if asn in networks_dict:
            networks_dict[asn].append(
                dict(
                    location=router_config["location"],
                    hostname=router_config["name"],
                    display_name=router_config["display_name"],
                )
            )
        else:
            networks_dict[asn] = [
                dict(
                    location=router_config["location"],
                    hostname=router_config["name"],
                    display_name=router_config["display_name"],
                )
            ]
    return networks_dict


def codes():
    """Reusable status code numbers"""
    code_dict = {
        # 200: renders standard display text
        "success": 200,
        # 405: Renders Bulma "warning" class notification message with message text
        "warning": 405,
        # 415: Renders Bulma "danger" class notification message with message text
        "danger": 415,
    }
    return code_dict


def codes_reason():
    """Reusable status code descriptions"""
    code_desc_dict = {
        200: "Valid Query",
        405: "Query Not Allowed",
        415: "Query Invalid",
    }
    return code_desc_dict


def scrape_list():
    """Returns list of configured network operating systems"""
    config_commands = toml.load(os.path.join(working_dir, "commands.toml"))
    scrape = []
    for nos in config_commands:
        scrape.append(nos)
    return scrape


def command(nos):
    """Associates input NOS with matched commands defined in commands.toml"""
    config_commands = toml.load(os.path.join(working_dir, "commands.toml"))
    commands = None
    if nos in scrape_list():
        commands = {
            "dual": config_commands[nos][0]["dual"],
            "ipv4": config_commands[nos][0]["ipv4"],
            "ipv6": config_commands[nos][0]["ipv6"],
        }
    return commands


def credential(cred):
    """Associates input credential key name with configured credential username & password in \
    devices.toml."""
    c_list = devices["credential"]
    return dict(username=c_list[cred]["username"], password=c_list[cred]["password"])


def device(dev):
    """Associates input device key name with configured device attributes in devices.toml"""
    device_config = devices["router"][dev]
    return dict(
        address=device_config.get("address"),
        asn=device_config.get("asn"),
        src_addr_ipv4=device_config.get("src_addr_ipv4"),
        src_addr_ipv6=device_config.get("src_addr_ipv6"),
        credential=device_config.get("credential"),
        location=device_config.get("location"),
        name=device_config.get("name"),
        display_name=device_config.get("display_name"),
        port=device_config.get("port"),
        type=device_config.get("type"),
        proxy=device_config.get("proxy"),
    )


def proxy(prx):
    """Associates input proxy key name with configured proxy attributes in devices.toml"""
    proxy_config = devices["proxy"][prx]
    return dict(
        address=proxy_config["address"],
        username=proxy_config["username"],
        password=proxy_config["password"],
        type=proxy_config["type"],
        ssh_command=proxy_config["ssh_command"],
    )


def general():
    """Exports general config variables and sets default values if undefined"""
    gen = configuration["general"]
    re_bgp_aspath_mode = gen["bgp_aspath"].get("mode", "asplain")
    if re_bgp_aspath_mode == "asplain":
        re_bgp_aspath_default = r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"
    if re_bgp_aspath_mode == "asdot":
        re_bgp_aspath_default = (
            r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"
        )
    return dict(
        primary_asn=gen.get("primary_asn", "65000"),
        org_name=gen.get("org_name", "The Company"),
        debug=gen.get("debug", False),
        google_analytics=gen.get("google_analytics", ""),
        msg_error_querytype=gen.get(
            "msg_error_querytype", "You must select a query type."
        ),
        msg_error_notallowed=gen.get(
            "msg_error_notallowed", "<b>{i}</b> is not allowed."
        ),
        msg_error_ipv6cidr=gen.get(
            "msg_error_ipv6cidr",
            "<b>{d}</b> requires IPv6 BGP lookups to be in CIDR notation.",
        ),
        msg_error_invalidip=gen.get(
            "msg_error_invalidip", "<b>{i}</b> is not a valid IP address."
        ),
        msg_error_invaliddual=gen.get(
            "msg_error_invaliddual", "<b>{i}</b> is an invalid {qt}."
        ),
        msg_error_general=gen.get("msg_error_general", "A general error occurred."),
        msg_error_directed_cidr=gen.get(
            "msg_error_directed_cidr", "<b>{cmd}</b> queries can not be in CIDR format."
        ),
        msg_max_prefix=gen.get(
            "msg_max_prefix",
            "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific.",
        ),
        rate_limit_query=gen.get("rate_limit_query", "5"),
        message_rate_limit_query=gen.get(
            "message_rate_limit_query",
            (
                f'Query limit of {gen.get("rate_limit_query", "5")} per minute reached. '
                "Please wait one minute and try again."
            ),
        ),
        enable_bgp_route=gen.get("enable_bgp_route", True),
        enable_bgp_community=gen.get("enable_bgp_community", True),
        enable_bgp_aspath=gen.get("enable_bgp_aspath", True),
        enable_ping=gen.get("enable_ping", True),
        enable_traceroute=gen.get("enable_traceroute", True),
        rate_limit_site=gen.get("rate_limit_site", "120"),
        cache_timeout=gen.get("cache_timeout", 120),
        cache_directory=gen.get(
            "cache_directory", os.path.join(hyperglass_root, ".flask_cache")
        ),
        enable_max_prefix=gen.get("enable_max_prefix", False),
        max_prefix_length_ipv4=gen.get("max_prefix_length_ipv4", 24),
        max_prefix_length_ipv6=gen.get("max_prefix_length_ipv6", 64),
        re_bgp_community_new=gen.get(
            "re_bgp_community_new", r"^([0-9]{0,5})\:([0-9]{1,5})$"
        ),
        re_bgp_community_32bit=gen.get("re_bgp_community_32bit", r"^[0-9]{1,10}$"),
        re_bgp_community_large=gen.get(
            "re_bgp_community_large", r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"
        ),
        re_bgp_aspath=gen["bgp_aspath"][re_bgp_aspath_mode].get(
            "regex", re_bgp_aspath_default
        ),
    )


def branding():
    """Exports branding config variables and sets default values if undefined"""
    brand = configuration["branding"]
    gen = general()
    return dict(
        site_title=brand.get("site_title", "hyperglass"),
        title=brand.get("title", "hyperglass"),
        subtitle=brand.get("subtitle", f'AS{gen["primary_asn"]}'),
        title_mode=brand.get("title_mode", "logo_only"),
        enable_footer=brand.get("enable_footer", True),
        enable_credit=brand.get("enable_credit", True),
        color_btn_submit=brand.get("color_btn_submit", "#40798c"),
        color_tag_loctitle=brand.get("color_tag_loctitle", "#330036"),
        color_tag_cmdtitle=brand.get("color_tag_cmdtitle", "#330036"),
        color_tag_cmd=brand.get("color_tag_cmd", "#ff5e5b"),
        color_tag_loc=brand.get("color_tag_loc", "#40798c"),
        color_progressbar=brand.get("color_progressbar", "#40798c"),
        color_bg=brand.get("color_bg", "#fbfffe"),
        color_danger=brand.get("color_danger", "#ff3860"),
        logo_path=brand.get(
            "logo_path",
            os.path.join(hyperglass_root, "static/images/hyperglass-dark.png"),
        ),
        logo_width=brand.get("logo_width", "384"),
        favicon_dir=brand.get("favicon_path", "static/images/favicon/"),
        placeholder_prefix=brand.get(
            "placeholder_prefix", "IP, Prefix, Community, or AS_PATH"
        ),
        show_peeringdb=brand.get("show_peeringdb", True),
        text_results=brand.get("text_results", "Results"),
        text_location=brand.get("text_location", "Select Location..."),
        text_cache=brand.get(
            "text_cache",
            f'Results will be cached for {math.ceil(gen["cache_timeout"] / 60)} minutes.',
        ),
        primary_font_name=brand.get("primary_font_name", "Nunito"),
        primary_font_url=brand.get(
            "primary_font_url",
            "https://fonts.googleapis.com/css?family=Nunito:400,600,700",
        ),
        mono_font_name=brand.get("mono_font_name", "Fira Mono"),
        mono_font_url=brand.get(
            "mono_font_url", "https://fonts.googleapis.com/css?family=Fira+Mono"
        ),
        text_limiter_title=brand.get("text_limiter_title", "Limit Reached"),
        text_limiter_subtitle=brand.get(
            "text_limiter_subtitle",
            (
                f'You have accessed this site more than {gen["rate_limit_site"]} '
                "times in the last minute."
            ),
        ),
        text_500_title=brand.get("text_500_title", "Error"),
        text_500_subtitle=brand.get("text_500_subtitle", "Something went wrong."),
        text_500_button=brand.get("text_500_button", "Home"),
        text_help_bgp_route=brand.get(
            "text_help_bgp_route",
            "Performs BGP table lookup based on IPv4/IPv6 prefix.",
        ),
        text_help_bgp_community=brand.get(
            "text_help_bgp_community",
            (
                'Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360">'
                'Extended</a> or <a href="https://tools.ietf.org/html/rfc8195">Large</a> '
                "community value.<br>"
                '<a href="#" onclick="bgpHelpCommunity()">BGP Communities</a>'
            ),
        ),
        text_help_bgp_aspath=brand.get(
            "text_help_bgp_aspath",
            (
                "Performs BGP table lookup based on <code>AS_PATH</code> regular expression."
                '<br>For commonly used BGP regular expressions, <a href="https://hyperglass.'
                'readthedocs.io/en/latest/Extras/common_as_path_regex/">click here</a>.<br>'
                '<a href="#" onclick="bgpHelpASPath()">Allowed BGP AS Path Expressions</a>'
            ),
        ),
        text_help_ping=brand.get(
            "text_help_ping", "Sends 5 ICMP echo requests to the target."
        ),
        text_help_traceroute=brand.get(
            "text_help_traceroute",
            (
                "Performs UDP Based traceroute to the target.<br>For information about how to"
                'interpret traceroute results, <a href="https://www.nanog.org/meetings/nanog45/'
                'presentations/Sunday/RAS_traceroute_N45.pdf">click here</a>.'
            ),
        ),
    )
