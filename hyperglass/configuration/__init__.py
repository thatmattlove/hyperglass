#!/usr/bin/env python3
import os
import math
import toml
import hyperglass

dir = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)


def blacklist():
    f = os.path.join(dir, "blacklist.toml")
    t = toml.load(f)
    return t


def commands():
    f = os.path.join(dir, "commands.toml")
    t = toml.load(f)
    return t


def configuration():
    f = os.path.join(dir, "configuration.toml")
    t = toml.load(f)
    return t


def devices():
    f = os.path.join(dir, "devices.toml")
    t = toml.load(f)
    return t


def requires_ipv6_cidr():
    f = os.path.join(dir, "requires_ipv6_cidr.toml")
    t = toml.load(f)
    return t["requires_ipv6_cidr"]


# Filter config to branding variables
branding = configuration()["branding"]

# Filter config to general variables
general = configuration()["general"]

routers_list = devices()["router"]


class dev:
    """Functions to import device variables"""

    def networks():
        asn_dict = dict()
        for r in routers_list:
            asn = r["asn"]
            if asn in asn_dict:
                asn_dict[asn].append(r["location"])
            else:
                asn_dict[asn] = [r["location"]]
        return asn_dict

    def name():
        list = []
        for r in routers_list:
            list.append(str(r["name"]))
        return list

    def display_name():
        list = []
        for r in routers_list:
            list.appen(str(r["display_name"]))
        return list


class gen:
    """Functions to import config variables and return default values if undefined"""

    def primary_asn():
        list = []
        for g in general:
            if len(g["primary_asn"]) == 0:
                return "65000"
            else:
                return g["primary_asn"]

    def org_name():
        list = []
        for g in general:
            if len(g["org_name"]) == 0:
                return "The Company"
            else:
                return g["org_name"]

    def debug():
        list = []
        for a in general:
            try:
                return a["debug"]
            except:
                return True

    def google_analytics():
        list = []
        for a in general:
            if len(a["google_analytics"]) == 0:
                return ""
            else:
                return a["google_analytics"]

    def enable_recaptcha():
        list = []
        for a in general:
            try:
                return a["enable_recaptcha"]
            except:
                return True

    def message_error():
        list = []
        for a in general:
            if len(a["message_error"]) == 0:
                return "{input} is invalid."
            else:
                return a["message_error"]

    def message_blacklist():
        list = []
        for a in general:
            if len(a["message_blacklist"]) == 0:
                return "{input} is not allowed."
            else:
                return a["message_blacklist"]

    def message_rate_limit_query():
        list = []
        for a in general:
            if len(a["message_rate_limit_query"]) == 0:
                return "Query limit of {rate_limit_query} per minute reached. Please wait one minute and try again.".format(
                    rate_limit_query=gen.rate_limit_query()
                )
            else:
                return a["message_rate_limit_query"]

    def enable_bgp_route():
        list = []
        for a in general:
            try:
                return a["enable_bgp_route"]
            except:
                return True

    def enable_bgp_community():
        list = []
        for a in general:
            try:
                return a["enable_bgp_community"]
            except:
                return True

    def enable_bgp_aspath():
        list = []
        for a in general:
            try:
                return a["enable_bgp_aspath"]
            except:
                return True

    def enable_ping():
        list = []
        for a in general:
            try:
                return a["enable_ping"]
            except:
                return True

    def enable_traceroute():
        list = []
        for a in general:
            try:
                return a["enable_traceroute"]
            except:
                return True

    def rate_limit_query():
        list = []
        for a in general:
            if len(a["rate_limit_query"]) == 0:
                return "5"
            else:
                return a["rate_limit_query"]

    def rate_limit_site():
        list = []
        for a in general:
            if len(a["rate_limit_site"]) == 0:
                return "120"
            else:
                return a["rate_limit_site"]

    def cache_timeout():
        list = []
        for a in general:
            try:
                return a["cache_timeout"]
            except:
                return 120

    def cache_directory():
        list = []
        for a in general:
            if len(a["cache_directory"]) == 0:
                d = ".flask_cache"
                return os.path.join(hyperglass_root, d)
            else:
                return a["cache_directory"]


class brand:
    """Functions to import branding variables and return default values if undefined"""

    def site_title():
        list = []
        for t in branding:
            if len(t["site_title"]) == 0:
                return "hyperglass"
            else:
                return t["site_title"]

    def title():
        list = []
        for t in branding:
            if len(t["title"]) == 0:
                return "hyperglass"
            else:
                return t["title"]

    def subtitle():
        list = []
        for t in branding:
            if len(t["subtitle"]) == 0:
                return "AS" + gen.primary_asn()
            else:
                return t["subtitle"]

    def title_mode():
        list = []
        for t in branding:
            if len(t["title_mode"]) == 0:
                return "logo_only"
            else:
                return t["title_mode"]

    def enable_footer():
        list = []
        for t in branding:
            try:
                return t["enable_footer"]
            except:
                return True

    def enable_credit():
        list = []
        for t in branding:
            try:
                return t["enable_credit"]
            except:
                return True

    def color_btn_submit():
        list = []
        for t in branding:
            if len(t["color_btn_submit"]) == 0:
                return "#40798c"
            else:
                return t["color_btn_submit"]

    def color_tag_loctitle():
        list = []
        for t in branding:
            if len(t["color_tag_loctitle"]) == 0:
                return "#330036"
            else:
                return t["color_tag_loctitle"]

    def color_tag_cmdtitle():
        list = []
        for t in branding:
            if len(t["color_tag_cmdtitle"]) == 0:
                return "#330036"
            else:
                return t["color_tag_cmdtitle"]

    def color_tag_cmd():
        list = []
        for t in branding:
            if len(t["color_tag_cmd"]) == 0:
                return "#ff5e5b"
            else:
                return t["color_tag_cmd"]

    def color_tag_loc():
        list = []
        for t in branding:
            if len(t["color_tag_loc"]) == 0:
                return "#40798c"
            else:
                return t["color_tag_loc"]

    def color_progressbar():
        list = []
        for t in branding:
            if len(t["color_progressbar"]) == 0:
                return "#40798c"
            else:
                return t["color_progressbar"]

    def color_bg():
        list = []
        for t in branding:
            if len(t["color_bg"]) == 0:
                return "#fbfffe"
            else:
                return t["color_bg"]

    def color_danger():
        list = []
        for t in branding:
            if len(t["color_danger"]) == 0:
                return "#ff3860"
            else:
                return t["color_danger"]

    def logo_path():
        list = []
        for t in branding:
            if len(t["logo_path"]) == 0:
                f = "static/images/hyperglass-dark.png"
                return os.path.join(hyperglass_root, f)
            else:
                return t["logo_path"]

    def favicon16_path():
        list = []
        for t in branding:
            if len(t["favicon16_path"]) == 0:
                f = "static/images/favicon/favicon-16x16.png"
                return f
            else:
                return t["favicon16_path"]

    def favicon32_path():
        list = []
        for t in branding:
            if len(t["favicon32_path"]) == 0:
                f = "static/images/favicon/favicon-32x32.png"
                return f
            else:
                return t["favicon32_path"]

    def logo_width():
        list = []
        for t in branding:
            if len(t["logo_width"]) == 0:
                return "384"
            else:
                return t["logo_width"]

    def placeholder_prefix():
        list = []
        for t in branding:
            if len(t["placeholder_prefix"]) == 0:
                return "Prefix, IP, Community, or AS_PATH"
            else:
                return t["placeholder_prefix"]

    def show_peeringdb():
        list = []
        for t in branding:
            try:
                return a["show_peeringdb"]
            except:
                return True

    def text_results():
        list = []
        for t in branding:
            if len(t["text_results"]) == 0:
                return "Results"
            else:
                return t["text_results"]

    def text_location():
        list = []
        for t in branding:
            if len(t["text_location"]) == 0:
                return "Location"
            else:
                return t["text_location"]

    def text_cache():
        list = []
        for t in branding:
            if len(t["text_cache"]) == 0:
                cache_timeout_exact = gen.cache_timeout() / 60
                return "Results will be cached for {cache_timeout} minutes.".format(
                    cache_timeout=math.ceil(cache_timeout_exact)
                )
            else:
                return t["text_cache"]

    def primary_font_url():
        list = []
        for t in branding:
            if len(t["primary_font_url"]) == 0:
                return "https://fonts.googleapis.com/css?family=Nunito:400,600,700"
            else:
                return t["primary_font_url"]

    def primary_font_name():
        list = []
        for t in branding:
            if len(t["primary_font_name"]) == 0:
                return "Nunito"
            else:
                return t["primary_font_name"]

    def mono_font_url():
        list = []
        for t in branding:
            if len(t["mono_font_url"]) == 0:
                return "https://fonts.googleapis.com/css?family=Fira+Mono"
            else:
                return t["mono_font_url"]

    def mono_font_name():
        list = []
        for t in branding:
            if len(t["mono_font_name"]) == 0:
                return "Fira Mono"
            else:
                return t["mono_font_name"]

    def text_limiter_title():
        list = []
        for t in branding:
            if len(t["text_limiter_title"]) == 0:
                return "Limit Reached"
            else:
                return t["text_limiter_title"]

    def text_limiter_subtitle():
        list = []
        for t in branding:
            if len(t["text_limiter_subtitle"]) == 0:
                return "You have accessed this site more than {rate_limit_site} times in the last minute.".format(
                    rate_limit_site=gen.rate_limit_site()
                )
            else:
                return t["text_limiter_subtitle"]

    def text_415_title():
        list = []
        for t in branding:
            if len(t["text_415_title"]) == 0:
                return "Error"
            else:
                return t["text_415_title"]

    def text_415_subtitle():
        list = []
        for t in branding:
            if len(t["text_415_subtitle"]) == 0:
                return "Something went wrong."
            else:
                return t["text_415_subtitle"]

    def text_415_button():
        list = []
        for t in branding:
            if len(t["text_415_button"]) == 0:
                return "Home"
            else:
                return t["text_415_button"]

    def text_help_bgp_route():
        list = []
        for t in branding:
            if len(t["text_help_bgp_route"]) == 0:
                return "Performs BGP table lookup based on IPv4/IPv6 prefix."
            else:
                return t["text_help_bgp_route"]

    def text_help_bgp_community():
        list = []
        for t in branding:
            if len(t["text_help_bgp_community"]) == 0:
                return 'Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195">Large</a> community value.'
            else:
                return t["text_help_bgp_community"]

    def text_help_bgp_aspath():
        list = []
        for t in branding:
            if len(t["text_help_bgp_aspath"]) == 0:
                return 'Performs BGP table lookup based on <code>AS_PATH</code> regular expression.<br>For commonly used BGP regular expressions, <a href="https://hyperglass.readthedocs.io/en/latest/Extras/common_as_path_regex/">click here</a>.'
            else:
                return t["text_help_bgp_aspath"]

    def text_help_ping():
        list = []
        for t in branding:
            if len(t["text_help_ping"]) == 0:
                return "Sends 5 ICMP echo requests to the target."
            else:
                return t["text_help_ping"]

    def text_help_traceroute():
        list = []
        for t in branding:
            if len(t["text_help_traceroute"]) == 0:
                return 'Performs UDP Based traceroute to the target.<br>For information about how to interpret traceroute results, <a href="https://www.nanog.org/meetings/nanog45/presentations/Sunday/RAS_traceroute_N45.pdf">click here</a>.'
            else:
                return t["text_help_traceroute"]
