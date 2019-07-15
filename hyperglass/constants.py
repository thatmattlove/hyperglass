"""
Global Constants for hyperglass
"""

protocol_map = {80: "http", 8080: "http", 443: "https", 8443: "https"}


class Status:
    """
    Defines codes, messages, and method names for status codes used by
    hyperglass.
    """

    codes_dict = {
        200: ("valid", "Valid Query"),
        405: ("not_allowed", "Query Not Allowed"),
        415: ("invalid", "Invalid Query"),
        504: ("target_error", "Unable to Reach Target"),
    }

    def __init__(self):
        """
        Dynamically generates class attributes for codes in codes_dict.
        """
        for (_code, text) in Status.codes_dict.items():
            setattr(self, text[0], _code)

    @staticmethod
    def get_reason(search_code):
        """
        Maps and returns input code integer to associated reason text.
        Mainly used for populating Prometheus fields.
        """
        reason = None
        for (_code, text) in Status.codes_dict.items():
            if _code == search_code:
                reason = text[1]
        return reason


code = Status()


class Supported:
    """
    Defines items supported by hyperglass.

    query_types: Supported query types used to validate Flask input.

    rest: Supported REST API platforms

    scrape: Supported "scrape" platforms which will be accessed via
    Netmiko. List updated 07/2019.
    """

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
