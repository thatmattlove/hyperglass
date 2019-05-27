# Module Imports
import re
import sys
import json
import toml
from logzero import logger
from netaddr import IPNetwork, IPAddress, IPSet

# Project Imports
from hyperglass import configuration


code = configuration.codes()


def frr(cmd, ipprefix, device):
    """Validates input and constructs API call to FRRouting Stack via hyperglass-frr API"""
    d_address = device["address"]
    d_src_addr_ipv4 = device["src_addr_ipv4"]
    d_src_addr_ipv6 = device["src_addr_ipv6"]
    d_location = device["location"]
    d_name = device["name"]
    d_port = device["port"]
    d_type = device["type"]

    # BGP Community Query
    if cmd in ["bgp_community"]:
        # Extended Communities, new-format
        query = json.dumps({"cmd": cmd, "afi": "dual", "target": ipprefix})
        if re.match("^([0-9]{0,5})\:([0-9]{1,5})$", ipprefix):
            msg = f"{ipprefix} matched new-format community."
            return (msg, code.success, d_address, query)
        # Extended Communities, 32 bit format
        elif re.match("^[0-9]{1,10}$", ipprefix):
            msg = f"{ipprefix} matched 32 bit community."
            return (msg, code.success, d_address, query)
        # RFC 8092 Large Community Support
        elif re.match("^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$", ipprefix):
            msg = f"{ipprefix} matched large community."
            return (msg, code.success, d_address, query)
        else:
            msg = f"{ipprefix} is an invalid BGP Community Format."
            logger.error(f"{msg}, {code.danger}, {d_name}, {query}")
            return (msg, code.danger, d_address, query)
    # BGP AS_PATH Query
    elif cmd in ["bgp_aspath"]:
        if re.match(".*", ipprefix):
            query = json.dumps({"cmd": cmd, "afi": "dual", "target": ipprefix})
            msg = f"{ipprefix} matched AS_PATH regex."
            return (msg, code.success, d_address, query)
        else:
            msg = f"{ipprefix} is an invalid AS_PATH regex."
            logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
            return (msg, code.danger, d_address, query)
    # BGP Route Query
    elif cmd in ["bgp_route"]:
        try:
            # Use netaddr library to verify if input is a valid IPv4 address or prefix
            if IPNetwork(ipprefix).ip.version == 4:
                query = json.dumps({"cmd": cmd, "afi": "ipv4", "target": ipprefix})
                msg = f"{ipprefix} is a valid IPv4 Adddress."
                return (msg, code.success, d_address, query)
            # Use netaddr library to verify if input is a valid IPv6 address or prefix
            elif IPNetwork(ipprefix).ip.version == 6:
                query = json.dumps({"cmd": cmd, "afi": "ipv6", "target": ipprefix})
                msg = f"{ipprefix} is a valid IPv6 Adddress."
                return (msg, code.success, d_address, query)
        # Exception from netaddr library will return a user-facing error
        except:
            msg = f"{ipprefix} is an invalid IP Address."
            logger.error(f"{msg}, {code.danger}, {d_name}, {query}")
            return (msg, code.danger, d_address, query)
    # Ping/Traceroute
    elif cmd in ["ping", "traceroute"]:
        try:
            if IPNetwork(ipprefix).ip.version == 4:
                query = json.dumps(
                    {
                        "cmd": cmd,
                        "afi": "ipv4",
                        "source": d_src_addr_ipv4,
                        "target": ipprefix,
                    }
                )
                msg = f"{ipprefix} is a valid IPv4 Adddress."
                return (msg, code.success, d_address, query)
            elif IPNetwork(ipprefix).ip.version == 6:
                query = json.dumps(
                    {
                        "cmd": cmd,
                        "afi": "ipv6",
                        "source": d_src_addr_ipv6,
                        "target": ipprefix,
                    }
                )
                msg = f"{ipprefix} is a valid IPv6 Adddress."
                return (msg, code.success, d_address, query)
        except:
            msg = f"{ipprefix} is an invalid IP Address."
            logger.error(f"{msg}, {code.danger}, {d_name}, {query}")
            return (msg, code.danger, d_name, query)
    else:
        msg = f"Command {cmd} not found."
        logger.error(f"{msg}, {code.danger}, {d_name}, {query}")
        return (msg, code.danger, d_name, query)


def ssh(cmd, ipprefix, device):
    """Validates input and constructs usable commands to run via netmiko"""
    d_address = device["address"]
    d_src_addr_ipv4 = device["src_addr_ipv4"]
    d_src_addr_ipv6 = device["src_addr_ipv6"]
    d_location = device["location"]
    d_name = device["name"]
    d_port = device["port"]
    d_type = device["type"]

    c = configuration.command(d_type)
    # BGP Community Query
    if cmd == "bgp_community":
        # Extended Communities, new-format
        if re.match("^([0-9]{0,5})\:([0-9]{1,5})$", ipprefix):
            mc = c.dual[cmd]
            command = mc.format(target=ipprefix)
            msg = f"{ipprefix} matched new-format community."
            return (msg, code.success, d_address, d_type, command)
        # Extended Communities, 32 bit format
        elif re.match("^[0-9]{1,10}$", ipprefix):
            mc = c.dual[cmd]
            command = mc.format(target=ipprefix)
            msg = f"{ipprefix} matched 32 bit community."
            return (msg, code.success, d_address, d_type, command)
        # RFC 8092 Large Community Support
        elif re.match("^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$", ipprefix):
            mc = c.dual[cmd]
            command = mc.format(target=ipprefix)
            msg = f"{ipprefix} matched large community."
            return (msg, code.success, d_address, d_type, command)
        else:
            msg = f"{ipprefix} is an invalid BGP Community Format."
            logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
            return (msg, code.danger, d_name, cmd, ipprefix)
    # BGP AS_PATH Query
    elif cmd == "bgp_aspath":
        if re.match(".*", ipprefix):
            mc = c.dual[cmd]
            command = mc.format(target=ipprefix)
            msg = f"{ipprefix} matched AS_PATH regex."
            return (msg, code.success, d_address, d_type, command)
        else:
            msg = f"{ipprefix} is an invalid AS_PATH regex."
            logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
            return (msg, code.danger, d_name, cmd, ipprefix)
    # BGP Route Query
    elif cmd == "bgp_route":
        try:
            # Use netaddr library to verify if input is a valid IPv4 address or prefix
            if IPNetwork(ipprefix).ip.version == 4:
                mc = c.ipv4[cmd]
                command = mc.format(target=ipprefix)
                msg = f"{ipprefix} is a valid IPv4 Adddress."
                return (msg, code.success, d_address, d_type, command)
                # Use netaddr library to verify if input is a valid IPv6 address or prefix
            elif IPNetwork(ipprefix).ip.version == 6:
                mc = c.ipv6[cmd]
                command = mc.format(target=ipprefix)
                msg = f"{ipprefix} is a valid IPv6 Adddress."
                return (msg, code.success, d_address, d_type, command)
        # Exception from netaddr library will return a user-facing error
        except:
            msg = f"{ipprefix} is an invalid IP Address."
            logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
            return (msg, code.danger, d_name, cmd, ipprefix)
    # Ping/Traceroute
    elif cmd in ["ping", "traceroute"]:
        try:
            if IPNetwork(ipprefix).ip.version == 4:
                mc = c.ipv4[cmd]
                command = mc.format(target=ipprefix, src_addr_ipv4=d_src_addr_ipv4)
                msg = f"{ipprefix} is a valid IPv4 Adddress."
                return (msg, code.success, d_address, d_type, command)
            elif IPNetwork(ipprefix).ip.version == 6:
                mc = c.ipv6[cmd]
                command = mc.format(target=ipprefix, src_addr_ipv6=d_src_addr_ipv6)
                msg = f"{ipprefix} is a valid IPv6 Adddress."
                return (msg, code.success, d_address, d_type, command)
        except:
            msg = f"{ipprefix} is an invalid IP Address."
            logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
            return (msg, code.danger, d_name, cmd, ipprefix)
    else:
        msg = f"Command {cmd} not found."
        logger.error(f"{msg}, {code.danger}, {d_name}, {cmd}, {ipprefix}")
        return (msg, code.danger, d_name, cmd, ipprefix)
