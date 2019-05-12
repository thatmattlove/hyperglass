import re
import sys
import toml
import logging
from netaddr import *
from logzero import logger

# Local imports
from hyperglass import configuration

# Load TOML config file
devices = configuration.devices()

# Load TOML commands file
commands = configuration.commands()

# Filter config to router list
routers_list = devices["router"]

# Receives JSON from Flask, constucts the command that will be passed to the router
# Also handles input validation & error handling
def construct(router, cmd, ipprefix):
    logger.info(f"Constructing {cmd} command for {router} to {ipprefix}...")
    try:
        # Loop through routers config file, match input router with configured routers, set variables
        for r in routers_list:
            try:
                if router == r["address"]:
                    type = r["type"]
                    src_addr_ipv4 = r["src_addr_ipv4"]
                    src_addr_ipv6 = r["src_addr_ipv6"]
                    # Loop through commands config file, set variables for matched commands
                    for nos in commands:
                        if type == nos:
                            nos = commands[type]
                            nos_commands = nos[0]
                            # Dual stack commands (agnostic of IPv4/IPv6)
                            dual_commands = nos_commands["dual"]
                            # IPv4 Specific Commands
                            ipv4_commands = nos_commands["ipv4"]
                            # IPv6 Specific Commands
                            ipv6_commands = nos_commands["ipv6"]
                            if cmd == "Query Type":
                                msg = "You must select a query type."
                                code = 415
                                logger.error(
                                    f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                )
                                return (msg, code, router, cmd, ipprefix)
                            # BGP Community Query
                            elif cmd in ["bgp_community"]:
                                # Extended Communities, new-format
                                if re.match("^([0-9]{0,5})\:([0-9]{1,5})$", ipprefix):
                                    for a, c in dual_commands.items():
                                        if a == cmd:
                                            command = c.format(target=ipprefix)
                                            msg = f"{ipprefix} matched new-format community."
                                            code = 200
                                            return (msg, code, router, type, command)
                                # Extended Communities, 32 bit format
                                elif re.match("^[0-9]{1,10}$", ipprefix):
                                    for a, c in dual_commands.items():
                                        if a == cmd:
                                            command = c.format(target=ipprefix)
                                            msg = (
                                                f"{ipprefix} matched 32 bit community."
                                            )
                                            code = 200
                                            return (msg, code, router, type, command)
                                # RFC 8092 Large Community Support
                                elif re.match(
                                    "^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$",
                                    ipprefix,
                                ):
                                    for a, c in dual_commands.items():
                                        if a == cmd:
                                            command = c.format(target=ipprefix)
                                            msg = f"{ipprefix} matched large community."
                                            code = 200
                                            return (msg, code, router, type, command)
                                else:
                                    msg = f"{ipprefix} is an invalid BGP Community Format."
                                    code = 415
                                    logger.error(
                                        f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                    )
                                    return (msg, code, router, cmd, ipprefix)
                            # BGP AS_PATH Query
                            elif cmd in ["bgp_aspath"]:
                                if re.match(".*", ipprefix):
                                    for a, c in dual_commands.items():
                                        if a == cmd:
                                            command = c.format(target=ipprefix)
                                            msg = f"{ipprefix} matched AS_PATH regex."
                                            code = 200
                                            return (msg, code, router, type, command)
                                else:
                                    msg = f"{ipprefix} is an invalid AS_PATH regex."
                                    code = 415
                                    logger.error(
                                        f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                    )
                                    return (msg, code, router, cmd, ipprefix)
                            # BGP Route Query
                            elif cmd in ["bgp_route"]:
                                try:
                                    # Use netaddr library to verify if input is a valid IPv4 address or prefix
                                    if IPNetwork(ipprefix).ip.version == 4:
                                        for a, c in ipv4_commands.items():
                                            if a == cmd:
                                                command = c.format(target=ipprefix)
                                                msg = f"{ipprefix} is a valid IPv4 Adddress."
                                                code = 200
                                                return (
                                                    msg,
                                                    code,
                                                    router,
                                                    type,
                                                    command,
                                                )
                                                # Use netaddr library to verify if input is a valid IPv6 address or prefix
                                    elif IPNetwork(ipprefix).ip.version == 6:
                                        for a, c in ipv6_commands.items():
                                            if a == cmd:
                                                command = c.format(target=ipprefix)
                                                msg = f"{ipprefix} is a valid IPv6 Adddress."
                                                code = 200
                                                return (
                                                    msg,
                                                    code,
                                                    router,
                                                    type,
                                                    command,
                                                )
                                # Exception from netaddr library will return a user-facing error
                                except:
                                    msg = f"{ipprefix} is an invalid IP Address."
                                    code = 415
                                    logger.error(
                                        f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                    )
                                    return (msg, code, router, cmd, ipprefix)
                            # Ping/Traceroute
                            elif cmd in ["ping", "traceroute"]:
                                try:
                                    if IPNetwork(ipprefix).ip.version == 4:
                                        for a, c in ipv4_commands.items():
                                            if a == cmd:
                                                command = c.format(
                                                    target=ipprefix,
                                                    src_addr_ipv4=src_addr_ipv4,
                                                )
                                                msg = f"{ipprefix} is a valid IPv4 Adddress."
                                                code = 200
                                                return (
                                                    msg,
                                                    code,
                                                    router,
                                                    type,
                                                    command,
                                                )
                                    elif IPNetwork(ipprefix).ip.version == 6:
                                        for a, c in ipv6_commands.items():
                                            if a == cmd:
                                                command = c.format(
                                                    target=ipprefix,
                                                    src_addr_ipv6=src_addr_ipv6,
                                                )
                                                msg = f"{ipprefix} is a valid IPv6 Adddress."
                                                code = 200
                                                return (
                                                    msg,
                                                    code,
                                                    router,
                                                    type,
                                                    command,
                                                )
                                except:
                                    msg = f"{ipprefix} is an invalid IP Address."
                                    code = 415
                                    logger.error(
                                        f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                    )
                                    return (msg, code, router, cmd, ipprefix)
                            else:
                                msg = f"Command {cmd} not found."
                                code = 415
                                logger.error(
                                    f"{msg}, {code}, {router}, {cmd}, {ipprefix}"
                                )
                                return (msg, code, router, cmd, ipprefix)
            except:
                router_ip = r["address"]
                error_msg = logger.error(
                    f"Input router IP {router} does not match the configured router IP of {router_ip}"
                )
                raise ValueError(error_msg)
    except:
        raise
