# https://github.com/checktheroads/hyperglass
"""
Imports configuration varibles from configuration files and returns default values if undefined.
"""
# Standard Imports
import os
import math
import logging

# Module Imports
import toml
import logzero
from logzero import logger

# Project Imports
import hyperglass

# Project Directories
working_dir = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)

# TOML Imports
config = toml.load(os.path.join(working_dir, "configuration.toml"))
devices = toml.load(os.path.join(working_dir, "devices.toml"))


def debug_state():
    """Returns string for logzero log level"""
    state = config.get("debug", False)
    return state


# Logzero Configuration
if debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)


def blacklist():
    """Returns list of subnets/IPs defined in blacklist.toml"""
    blacklist_config = config["blacklist"]
    return blacklist_config


def requires_ipv6_cidr(nos):
    """Returns boolean for input NOS association with the NOS list defined in \
    requires_ipv6_cidr.toml"""
    nos_list = config["requires_ipv6_cidr"]
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


def hostnames():
    """Returns list of all router hostnames for input validation"""
    hostname_list = []
    routers_list = devices["router"]
    for router in routers_list:
        hostname_list.append(router)
    return hostname_list


def locations_list():
    """Returns a dictionary of ASNs as keys, list of associated locations, router hostnames, and \
    router display names as keys. Used by Flask to populate the /routers/<asn> route, which is \
    ingested by a JS Ajax call to populate the list of locations associated with the selected \
    network/ASN on the main page."""
    networks_dict = {}
    routers_list = devices["router"]
    for router in routers_list:
        asn = routers_list[router]["asn"]
        if asn in networks_dict:
            networks_dict[asn].append(
                dict(
                    location=routers_list[router]["location"],
                    hostname=router,
                    display_name=routers_list[router]["display_name"],
                )
            )
        else:
            networks_dict[asn] = [
                dict(
                    location=routers_list[router]["location"],
                    hostname=router,
                    display_name=routers_list[router]["display_name"],
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


def rest_list():
    """Returns list of supported hyperglass API types"""
    rest = ["frr"]
    return rest


def scrape_list():
    """Returns list of configured network operating systems"""
    config_commands = toml.load(os.path.join(working_dir, "commands.toml"))
    scrape = []
    for nos in config_commands:
        scrape.append(nos)
    return scrape


def supported_nos():
    """Combines scrape_list & rest_list for full list of supported network operating systems"""
    scrape = scrape_list()
    rest = rest_list()
    supported = scrape + rest
    return supported


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


def params():
    """Builds combined nested dictionary of all parameters defined in configuration.toml, and if \
    undefined, uses a default value"""
    # pylint: disable=too-many-statements
    # Dear PyLint, this function is intended to be long AF, because hyperglass is inteded to be \
    # customizable AF. It would also be silly AF to break this into multiple functions, and you'd \
    # probably still complain. <3 -ML
    general = {}
    branding = {}
    features = {}
    messages = {}
    general["primary_asn"] = config["general"].get("primary_asn", "65000")
    general["org_name"] = config["general"].get("org_name", "The Company")
    general["google_analytics"] = config["general"].get("google_analytics", "")
    general["redis_host"] = config["general"].get("redis_host", "localhost")
    general["redis_port"] = config["general"].get("redis_port", 6379)
    features["rate_limit"] = config["features"]["rate_limit"]
    features["rate_limit"]["redis_id"] = config["features"]["rate_limit"].get(
        "redis_id", 1
    )
    features["rate_limit"]["query"] = config["features"]["rate_limit"]["query"]
    features["rate_limit"]["query"]["rate"] = config["features"]["rate_limit"][
        "query"
    ].get("rate", 5)
    features["rate_limit"]["query"]["period"] = config["features"]["rate_limit"].get(
        "period", "minute"
    )
    features["rate_limit"]["query"]["title"] = config["features"]["rate_limit"][
        "query"
    ].get("title", "Query Limit Reached")
    features["rate_limit"]["query"]["message"] = config["features"]["rate_limit"][
        "query"
    ].get(
        "message",
        f"""Query limit of {features["rate_limit"]["query"]["rate"]} per \
        {features["rate_limit"]["query"]["period"]} reached. Please wait one minute and try \
        again.""",
    )
    features["rate_limit"]["query"]["button"] = config["features"]["rate_limit"][
        "query"
    ].get("button", "Try Again")

    features["rate_limit"]["message"] = config["features"]["rate_limit"].get(
        "message",
        f"""Query limit of {features["rate_limit"]["query"]} per minute reached. \
        Please wait one minute and try again.""",
    )
    features["rate_limit"]["site"] = config["features"]["rate_limit"]["site"]
    features["rate_limit"]["site"]["rate"] = config["features"]["rate_limit"][
        "site"
    ].get("rate", 60)
    features["rate_limit"]["site"]["period"] = config["features"]["rate_limit"][
        "site"
    ].get("period", "minute")
    features["rate_limit"]["site"]["title"] = config["features"]["rate_limit"][
        "site"
    ].get("title", "Limit Reached")
    features["rate_limit"]["site"]["subtitle"] = config["features"]["rate_limit"][
        "site"
    ].get(
        "subtitle",
        f'You have accessed this site more than {features["rate_limit"]["site"]["rate"]} '
        f'times in the last {features["rate_limit"]["site"]["period"]}.',
    )
    features["rate_limit"]["site"]["button"] = config["features"]["rate_limit"][
        "site"
    ].get("button", "Try Again")
    features["cache"] = config["features"]["cache"]
    features["cache"]["redis_id"] = config["features"]["cache"].get("redis_id", 0)
    features["cache"]["timeout"] = config["features"]["cache"].get("timeout", 120)
    features["cache"]["show_text"] = config["features"]["cache"].get("show_text", True)
    features["cache"]["text"] = config["features"]["cache"].get(
        "text",
        f'Results will be cached for {math.ceil(features["cache"]["timeout"] / 60)} minutes.',
    )
    features["bgp_route"] = config["features"]["bgp_route"]
    features["bgp_route"]["enable"] = config["features"]["bgp_route"].get(
        "enable", True
    )
    features["bgp_community"] = config["features"]["bgp_community"]
    features["bgp_community"]["enable"] = config["features"]["bgp_community"].get(
        "enable", True
    )
    features["bgp_community"]["regex"] = config["features"]["bgp_community"]["regex"]
    features["bgp_community"]["regex"]["decimal"] = config["features"]["bgp_community"][
        "regex"
    ].get("decimal", r"^[0-9]{1,10}$")
    features["bgp_community"]["regex"]["extended_as"] = config["features"][
        "bgp_community"
    ]["regex"].get("extended_as", r"^([0-9]{0,5})\:([0-9]{1,5})$")
    features["bgp_community"]["regex"]["large"] = config["features"]["bgp_community"][
        "regex"
    ].get("large", r"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$")
    features["bgp_aspath"] = config["features"]["bgp_aspath"]
    features["bgp_aspath"]["enable"] = config["features"]["bgp_aspath"].get(
        "enable", True
    )
    features["bgp_aspath"]["regex"] = config["features"]["bgp_aspath"]["regex"]
    features["bgp_aspath"]["regex"]["mode"] = config["features"]["bgp_aspath"][
        "regex"
    ].get("mode", "asplain")
    features["bgp_aspath"]["regex"]["asplain"] = config["features"]["bgp_aspath"][
        "regex"
    ].get("asplain", r"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$")
    features["bgp_aspath"]["regex"]["asdot"] = config["features"]["bgp_aspath"][
        "regex"
    ].get("asdot", r"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$")
    features["bgp_aspath"]["regex"]["pattern"] = config["features"]["bgp_aspath"][
        "regex"
    ].get(features["bgp_aspath"]["regex"]["mode"], None)
    features["ping"] = config["features"]["ping"]
    features["ping"]["enable"] = config["features"]["ping"].get("enable", True)
    features["traceroute"] = config["features"]["traceroute"]
    features["traceroute"]["enable"] = config["features"]["traceroute"].get(
        "enable", True
    )
    features["max_prefix"] = config["features"]["max_prefix"]
    features["max_prefix"]["enable"] = config["features"]["max_prefix"].get(
        "enable", False
    )
    features["max_prefix"]["ipv4"] = config["features"]["max_prefix"].get("ipv4", 24)
    features["max_prefix"]["ipv6"] = config["features"]["max_prefix"].get("ipv6", 64)
    features["max_prefix"]["message"] = config["features"]["max_prefix"].get(
        "message",
        "Prefix length must be smaller than /{m}. <b>{i}</b> is too specific.",
    )
    messages["no_query_type"] = config["messages"].get(
        "no_query_type", "Query Type must be specified."
    )
    messages["no_location"] = config["messages"].get(
        "no_location", "A location must be selected."
    )
    messages["no_input"] = config["messages"].get(
        "no_input", "A target must be specified"
    )
    messages["not_allowed"] = config["messages"].get(
        "not_allowed", "<b>{i}</b> is not allowed."
    )
    messages["requires_ipv6_cidr"] = config["messages"].get(
        "requires_ipv6_cidr",
        "<b>{d}</b> requires IPv6 BGP lookups to be in CIDR notation.",
    )
    messages["invalid_ip"] = config["messages"].get(
        "invalid_ip", "<b>{i}</b> is not a valid IP address."
    )
    messages["invalid_dual"] = config["messages"].get(
        "invalid_dual", "<b>{i}</b> is an invalid {qt}."
    )
    messages["general"] = config["messages"].get("general", "An error occurred.")
    messages["directed_cidr"] = config["messages"].get(
        "directed_cidr", "<b>{q}</b> queries can not be in CIDR format."
    )
    branding["site_name"] = config["branding"].get("site_name", "hyperglass")
    branding["footer"] = config["branding"]["footer"]
    branding["footer"]["enable"] = config["branding"]["footer"].get("enable", True)
    branding["credit"] = config["branding"]["credit"]
    branding["credit"]["enable"] = config["branding"]["credit"].get("enable", True)
    branding["peering_db"] = config["branding"]["peering_db"]
    branding["peering_db"]["enable"] = config["branding"]["peering_db"].get(
        "enable", True
    )
    branding["text"] = config["branding"]["text"]
    branding["text"]["query_type"] = config["branding"]["text"].get(
        "query_type", "Query Type"
    )
    branding["text"]["title_mode"] = config["branding"]["text"].get(
        "title_mode", "logo_only"
    )
    branding["text"]["title"] = config["branding"]["text"].get("title", "hyperglass")
    branding["text"]["subtitle"] = config["branding"]["text"].get(
        "subtitle", f'AS{general["primary_asn"]}'
    )
    branding["text"]["results"] = config["branding"]["text"].get("results", "Results")
    branding["text"]["location"] = config["branding"]["text"].get(
        "location", "Select Location..."
    )
    branding["text"]["query_placeholder"] = config["branding"]["text"].get(
        "query_placeholder", "IP, Prefix, Community, or AS Path"
    )
    branding["text"]["bgp_route"] = config["branding"]["text"].get(
        "bgp_route", "BGP Route"
    )
    branding["text"]["bgp_community"] = config["branding"]["text"].get(
        "bgp_community", "BGP Community"
    )
    branding["text"]["bgp_aspath"] = config["branding"]["text"].get(
        "bgp_aspath", "BGP AS Path"
    )
    branding["text"]["ping"] = config["branding"]["text"].get("ping", "Ping")
    branding["text"]["traceroute"] = config["branding"]["text"].get(
        "traceroute", "Traceroute"
    )
    branding["text"]["404"]["title"] = config["branding"]["text"]["404"].get(
        "title", "Error"
    )
    branding["text"]["404"]["subtitle"] = config["branding"]["text"]["404"].get(
        "subtitle", "Page Not Found"
    )
    branding["text"]["500"]["title"] = config["branding"]["text"]["500"].get(
        "title", "Error"
    )
    branding["text"]["500"]["subtitle"] = config["branding"]["text"]["500"].get(
        "subtitle", "Something Went Wrong"
    )
    branding["text"]["500"]["button"] = config["branding"]["text"]["500"].get(
        "button", "Home"
    )
    branding["logo"] = config["branding"]["logo"]
    branding["logo"]["path"] = config["branding"]["logo"].get(
        "path", "static/images/hyperglass-dark.png"
    )
    branding["logo"]["width"] = config["branding"]["logo"].get("width", 384)
    branding["logo"]["favicons"] = config["branding"]["logo"].get(
        "favicons", "static/images/favicon/"
    )
    branding["color"] = config["branding"]["color"]
    branding["color"]["background"] = config["branding"]["color"].get(
        "background", "#fbfffe"
    )
    branding["color"]["button_submit"] = config["branding"]["color"].get(
        "button_submit", "#40798c"
    )
    branding["color"]["danger"] = config["branding"]["color"].get("danger", "#ff3860")
    branding["color"]["progress_bar"] = config["branding"]["color"].get(
        "progress_bar", "#40798c"
    )
    branding["color"]["tag"]["type"] = config["branding"]["color"]["tag"].get(
        "type", "#ff5e5b"
    )
    branding["color"]["tag"]["type_title"] = config["branding"]["color"]["tag"].get(
        "type_title", "#330036"
    )
    branding["color"]["tag"]["location"] = config["branding"]["color"]["tag"].get(
        "location", "#40798c"
    )
    branding["color"]["tag"]["location_title"] = config["branding"]["color"]["tag"].get(
        "location_title", "#330036"
    )
    branding["font"] = config["branding"]["font"]
    branding["font"]["primary"] = config["branding"]["font"]["primary"]
    branding["font"]["primary"]["name"] = config["branding"]["font"]["primary"].get(
        "name", "Nunito"
    )
    branding["font"]["primary"]["url"] = config["branding"]["font"]["primary"].get(
        "url", "https://fonts.googleapis.com/css?family=Nunito:400,600,700"
    )
    branding["font"]["mono"] = config["branding"]["font"]["mono"]
    branding["font"]["mono"]["name"] = config["branding"]["font"]["mono"].get(
        "name", "Fira Mono"
    )
    branding["font"]["mono"]["url"] = config["branding"]["font"]["mono"].get(
        "url", "https://fonts.googleapis.com/css?family=Fira+Mono"
    )
    params_dict = dict(
        general=general, branding=branding, features=features, messages=messages
    )
    return params_dict
