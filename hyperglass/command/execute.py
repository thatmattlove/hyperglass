# Module Imports
import re
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


class ipcheck:
    def __init__(self):
        self.ipv4_host = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)?$"
        self.ipv4_cidr = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|2[0-9]|1[0-9]|[0-9])?$"
        self.ipv6_host = "^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))?$"
        self.ipv6_cidr = "^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/((1(1[0-9]|2[0-8]))|([0-9][0-9])|([0-9]))?$"

    def test(self, prefix):
        if IPNetwork(prefix).ip.version == 4:
            if re.match(self.ipv4_host, prefix):
                return {"protocol": "ipv4", "type": "host"}
            elif re.match(self.ipv4_cidr, prefix):
                return {"protocol": "ipv4", "type": "cidr"}

        if IPNetwork(prefix).ip.version == 6:
            if re.match(self.ipv6_host, prefix):
                return {"protocol": "ipv6", "type": "host"}
            if re.match(self.ipv6_cidr, prefix):
                return {"protocol": "ipv6", "type": "cidr"}


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

    # Initialize status code class, create global variable for reuse.
    global code
    code = configuration.codes()

    # Initialize general configuration parameters class, create global variable for reuse.
    global general
    general = configuration.general()

    # Validate prefix input with netaddr library
    if lg_cmd in ["bgp_route", "ping", "traceroute"]:
        msg = general.msg_error_invalidip.format(i=lg_ipprefix)
        try:
            # Initialize prefix regex check class
            ipc = ipcheck().test(lg_ipprefix)
            if IPNetwork(lg_ipprefix).ip.is_reserved():
                return (msg, code.danger, lg_data)
            elif IPNetwork(lg_ipprefix).ip.is_netmask():
                return (msg, code.danger, lg_data)
            elif IPNetwork(lg_ipprefix).ip.is_hostmask():
                return (msg, code.danger, lg_data)
            elif IPNetwork(lg_ipprefix).ip.is_loopback():
                return (msg, code.danger, lg_data)
            elif IPNetwork(lg_ipprefix).ip.is_unicast():
                pass
            else:
                return (msg, code.danger, lg_data)
        except:
            return (msg, code.danger, lg_data)

    if lg_cmd == "Query Type":
        return (general.msg_error_querytype, code.warning, lg_data)

    global d
    d = configuration.device(lg_router)

    # Checks if device type is on the requires_ipv6_cidr list
    requires_ipv6_cidr = configuration.requires_ipv6_cidr(d.type)

    # Check blacklist list for prefixes/IPs and return an error upon a match
    if lg_cmd in ["bgp_route", "ping", "traceroute"]:
        blacklist = IPSet(configuration.blacklist())
        msg = general.msg_error_notallowed.format(i=lg_ipprefix)
        if IPNetwork(lg_ipprefix).ip in blacklist:
            return (msg, code.warning, lg_data)
        if lg_cmd == "bgp_route" and IPNetwork(lg_ipprefix).version == 6:
            if requires_ipv6_cidr == True and ipc["type"] == "host":
                msg = general.msg_error_ipv6cidr.format(d=d.display_name)
                return (msg, code.warning, lg_data)
        if lg_cmd in ["ping", "traceroute"] and ipc["type"] == "cidr":
            return (msg, code.warning, lg_data)

    # If enable_max_prefix feature enabled, require BGP Route queries be smaller than prefix size limit
    if lg_cmd == "bgp_route" and general.enable_max_prefix == True:
        if (
            IPNetwork(lg_ipprefix).version == 4
            and IPNetwork(lg_ipprefix).prefixlen > general.max_prefix_length_ipv4
        ):
            msg = general.msg_max_prefix.format(
                m=general.max_prefix_length_ipv4, i=IPNetwork(lg_ipprefix)
            )
            return (msg, code.warning, lg_data)
        if (
            IPNetwork(lg_ipprefix).version == 6
            and IPNetwork(lg_ipprefix).prefixlen > general.max_prefix_length_ipv6
        ):
            msg = general.msg_max_prefix.format(
                m=general.max_prefix_length_ipv6, i=IPNetwork(lg_ipprefix)
            )
            return (msg, code.warning, lg_data)

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
