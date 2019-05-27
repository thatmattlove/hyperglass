# Module Imports
import sys
import json
import time
import requests
from logzero import logger
from netmiko import redispatch
from netmiko import ConnectHandler
from netaddr import IPNetwork, IPAddress, IPSet

# Project Imports
from hyperglass import configuration
from hyperglass.command import parse
from hyperglass.command import construct


class params:
    """Sends input parameters to construct module for use by execution functions"""

    class http:
        def __init__(self):
            self.msg, self.status, self.router, self.query = construct.frr(
                lg_cmd, lg_ipprefix, d()
            )

        def __call__(self):
            return vars(self)

    class ssh:
        def __init__(self):
            self.msg, self.status, self.router, self.type, self.command = construct.ssh(
                lg_cmd, lg_ipprefix, d()
            )

        def __call__(self):
            return vars(self)

        def nm_host(self):
            c = configuration.credential(d.credential)
            attr = {
                "host": self.router,
                "device_type": self.type,
                "username": c.username,
                "password": c.password,
                "global_delay_factor": 0.5,
            }
            return attr

        def nm_proxy(self):
            p = configuration.proxy(d.proxy)
            attr = {
                "host": p.address,
                "username": p.username,
                "password": p.password,
                "device_type": p.type,
                "global_delay_factor": 0.5,
            }
            return attr


class connect:
    class restapi:
        def frr():
            """Sends HTTP POST to router running the hyperglass-frr API"""
            http = params().http()
            c = configuration.credential(d.credential)
            try:
                headers = {"Content-Type": "application/json", "X-API-Key": c.password}
                json_query = json.dumps(http.query)
                frr_endpoint = f"http://{d.address}:{d.port}/frr"
                frr_response = requests.post(
                    frr_endpoint, headers=headers, data=json_query
                )
                return frr_response.text, frr_response.status_code
            except:
                raise

    class nm:
        def direct():
            """Connects to the router via netmiko library, return the command output"""
            ssh = params().ssh()
            nm_host = ssh.nm_host()
            nm_connect_direct = ConnectHandler(**nm_host)
            nm_output_direct = nm_connect_direct.send_command(ssh.command)
            return nm_output_direct

        def proxied(device_proxy):
            """Connects to the proxy server via netmiko library, then logs into the router via standard SSH"""
            ssh = params().ssh()
            nm_proxy = ssh.nm_proxy()
            nm_host = ssh.nm_host()
            dp = configuration.proxy(d.proxy)

            nm_connect_proxied = ConnectHandler(**nm_proxy)
            nm_ssh_command = dp.ssh_command.format(**nm_host) + "\n"

            nm_connect_proxied.write_channel(nm_ssh_command)
            time.sleep(1)
            proxy_output = nm_connect_proxied.read_channel()

            try:
                # Accept SSH key warnings
                if "Are you sure you want to continue connecting" in proxy_output:
                    nm_connect_proxied.write_channel("yes" + "\n")
                    nm_connect_proxied.write_channel(nm_host["password"] + "\n")
                # Send password on prompt
                elif "assword" in proxy_output:
                    nm_connect_proxied.write_channel(nm_host["password"] + "\n")
                    proxy_output += nm_connect_proxied.read_channel()
                # Reclassify netmiko connection as configured device type
                redispatch(nm_connect_proxied, nm_host["device_type"])

                host_output = nm_connect_proxied.send_command(ssh.command)

                if host_output:
                    return host_output
            except:
                msg = f'Proxy server {nm_proxy["host"]} unable to reach target {nm_host["host"]}'
                logger.error(f"{msg}, {code.danger}, {lg_params}")
                raise
                return (general.message_general_error, code.danger, lg_params)


def execute(lg_data):
    """Ingests user input, runs blacklist check, runs prefix length check (if enabled),
    pulls all configuraiton variables for the input router."""
    logger.info(f"Received lookup request for: {lg_data}")
    # Create global variables for POSTed JSON from main app
    global lg_router
    lg_router = lg_data["router"]

    global lg_cmd
    lg_cmd = lg_data["cmd"]

    global lg_ipprefix
    lg_ipprefix = lg_data["ipprefix"]

    global lg_params
    lg_params = lg_data

    # Initialize general configuration parameters class, create global variable for reuse.
    global general
    general = configuration.general()

    # Initialize status code class, create global variable for reuse.
    global code
    code = configuration.codes()

    # Check blacklist list for prefixes/IPs and return an error upon a match
    if lg_cmd in ["bgp_route", "ping", "traceroute"]:
        try:
            blacklist = IPSet(configuration.blacklist())
            if IPNetwork(lg_ipprefix).ip in blacklist:
                msg = f"{lg_ipprefix} is not allowed."
                return (msg, code.warning, lg_data)
        # If netaddr library throws an exception, return a user-facing error.
        except:
            msg = f"{lg_ipprefix} is not a valid IP Address."
            return (msg, code.danger, lg_data)
    # If enable_max_prefix feature enabled, require BGP Route queries be smaller than prefix size limit
    if lg_cmd == "bgp_route" and general.enable_max_prefix == True:
        try:
            if (
                IPNetwork(lg_ipprefix).version == 4
                and IPNetwork(lg_ipprefix).prefixlen > general.max_prefix_length_ipv4
            ):
                msg = f"Prefix length must be smaller than /{general.max_prefix_length_ipv4}. {IPNetwork(lg_ipprefix)} is too specific."
                return (msg, code.warning, lg_data)
            if (
                IPNetwork(lg_ipprefix).version == 6
                and IPNetwork(lg_ipprefix).prefixlen > general.max_prefix_length_ipv6
            ):
                msg = f"Prefix length must be smaller than /{general.max_prefix_length_ipv4}. {IPNetwork(lg_ipprefix)} is too specific."
                return (msg, code.warning, lg_data)
        except:
            raise
    elif lg_cmd == "Query Type":
        msg = "You must select a query type."
        logger.error(f"{msg}, {code.danger}, {lg_data}")
        return (msg, code.danger, lg_data)

    global d
    d = configuration.device(lg_router)

    if d.type == "frr":
        http = params().http()
        try:
            if http.status in range(200, 300):
                output, frr_status = connect.restapi.frr()
                parsed_output = parse.parse(output, d.type, lg_cmd)
                return parsed_output, frr_status, http()
            elif http.status in range(400, 500):
                return http.msg, http.status, http()
            else:
                logger.error(general.message_general_error, 500, http())
                return general.message_general_error, 500, http()
        except:
            raise
    else:
        try:
            ssh = params().ssh()
            if ssh.status in range(200, 300):
                if d.proxy:
                    output = connect.nm.proxied(d.proxy)
                    parsed_output = parse.parse(output, d.type, lg_cmd)
                    return parsed_output, ssh.status, ssh.router, ssh.command
                elif not d.proxy:
                    output = connect.nm.direct()
                    parsed_output = parse.parse(output, d.type, lg_cmd)
                    return parsed_output, ssh.status, ssh.router, ssh.command
            elif ssh.status in range(400, 500):
                return ssh.msg, ssh.status, ssh()
            else:
                logger.error(general.message_general_error, 500, ssh())
                return general.message_general_error, 500, ssh()
        except:
            raise
