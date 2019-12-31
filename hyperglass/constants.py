"""Constant definitions used throughout the application."""
# Standard Library Imports
import sys

MIN_PYTHON_VERSION = (3, 7)

protocol_map = {80: "http", 8080: "http", 443: "https", 8443: "https"}

target_format_space = ("huawei", "huawei_vrpv8")

LOG_FMT = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} {time:HH:mm:ss} <lw>|</lw> {name}<lw>:</lw>"
    "<b>{line}</b> <lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)
LOG_LEVELS = [
    {"name": "DEBUG", "no": 10, "color": "<c>"},
    {"name": "INFO", "no": 20, "color": "<le>"},
    {"name": "SUCCESS", "no": 25, "color": "<g>"},
    {"name": "WARNING", "no": 30, "color": "<y>"},
    {"name": "ERROR", "no": 40, "color": "<y>"},
    {"name": "CRITICAL", "no": 50, "color": "<r>"},
]

LOG_HANDLER = {"sink": sys.stdout, "format": LOG_FMT, "level": "INFO"}


class Supported:
    """
    Defines items supported by hyperglass.

    query_types: Supported query types used to validate Flask input.

    rest: Supported REST API platforms

    scrape: Supported "scrape" platforms which will be accessed via
    Netmiko. List updated 07/2019.
    """

    query_parameters = ("query_location", "query_type", "query_target", "query_vrf")

    query_types = ("bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute")

    rest = ("frr", "bird")

    scrape = (
        "a10",
        "accedian",
        "alcatel_aos",
        "alcatel_sros",
        "apresia_aeos",
        "arista_eos",
        "aruba_os",
        "avaya_ers",
        "avaya_vsp",
        "brocade_fastiron",
        "brocade_netiron",
        "brocade_nos",
        "brocade_vdx",
        "brocade_vyos",
        "checkpoint_gaia",
        "calix_b6",
        "ciena_saos",
        "cisco_asa",
        "cisco_ios",
        "cisco_ios_telnet",
        "cisco_nxos",
        "cisco_s300",
        "cisco_tp",
        "cisco_wlc",
        "cisco_xe",
        "cisco_xr",
        "coriant",
        "dell_dnos9",
        "dell_force10",
        "dell_os6",
        "dell_os9",
        "dell_os10",
        "dell_powerconnect",
        "dell_isilon",
        "eltex",
        "enterasys",
        "extreme",
        "extreme_ers",
        "extreme_exos",
        "extreme_netiron",
        "extreme_nos",
        "extreme_slx",
        "extreme_vdx",
        "extreme_vsp",
        "extreme_wing",
        "f5_ltm",
        "f5_tmsh",
        "f5_linux",
        "fortinet",
        "generic_termserver",
        "hp_comware",
        "hp_procurve",
        "huawei",
        "huawei_vrpv8",
        "ipinfusion_ocnos",
        "juniper",
        "juniper_junos",
        "linux",
        "mellanox",
        "mrv_optiswitch",
        "netapp_cdot",
        "netscaler",
        "ovs_linux",
        "paloalto_panos",
        "pluribus",
        "quanta_mesh",
        "rad_etx",
        "ruckus_fastiron",
        "ubiquiti_edge",
        "ubiquiti_edgeswitch",
        "vyatta_vyos",
        "vyos",
        "oneaccess_oneos",
    )

    @staticmethod
    def is_supported(nos):
        """
        Returns boolean state of input Network Operating System against
        rest OR scrape tuples.
        """
        return bool(nos in Supported.rest + Supported.scrape)

    @staticmethod
    def is_scrape(nos):
        """
        Returns boolean state of input Network Operating System against
        scrape tuple.
        """
        return bool(nos in Supported.scrape)

    @staticmethod
    def is_rest(nos):
        """
        Returns boolean state of input Network Operating System against
        rest tuple.
        """
        return bool(nos in Supported.rest)

    @staticmethod
    def is_supported_query(query_type):
        """
        Returns boolean state of input Network Operating System against
        query_type tuple.
        """
        return bool(query_type in Supported.query_types)

    @staticmethod
    def map_transport(nos):
        """
        Returns "scrape" if input nos is in Supported.scrape tuple, or
        "rest" if input nos is in Supported.rest tuple.
        """
        transport = None
        if nos in Supported.scrape:
            transport = "scrape"
        elif nos in Supported.rest:
            transport = "rest"
        return transport

    @staticmethod
    def map_rest(nos):
        uri_map = {"frr": "frr", "bird": "bird"}
        return uri_map.get(nos)
