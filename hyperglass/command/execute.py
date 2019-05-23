#!/usr/bin/env python3

import sys
import json
import time
import requests
from netaddr import *
from logzero import logger
from netmiko import redispatch
from netmiko import ConnectHandler
from hyperglass import configuration
from hyperglass.command import parse
from hyperglass.command import construct

# Load TOML devices file
devices = configuration.devices()
# Filter config to router list
routers_list = devices["router"]
# Filter config to credential list
credentials_list = devices["credential"]
# Filter config to proxy servers
proxies_list = devices["proxy"]

blacklist_config = configuration.blacklist()
blacklist = IPSet(blacklist_config["blacklist"])

general_error = "Error connecting to device."


class device:
    def __init__(self, lg_router):
        for r in routers_list:
            if r["location"] == lg_router:
                self.address = r["address"]
                self.asn = r["asn"]
                self.src_addr_ipv4 = r["src_addr_ipv4"]
                self.src_addr_ipv6 = r["src_addr_ipv6"]
                self.credential = r["credential"]
                self.location = r["location"]
                self.name = r["name"]
                self.port = r["port"]
                self.type = r["type"]
                self.proxy = r["proxy"]

    def __call__(self):
        return vars(self)


class credential:
    def __init__(self, cred):
        if cred in credentials_list:
            self.username = credentials_list[cred]["username"]
            self.password = credentials_list[cred]["password"]


class proxy:
    def __init__(self, proxy):
        if proxy in proxies_list:
            self.address = proxies_list[proxy]["address"]
            self.username = proxies_list[proxy]["username"]
            self.password = proxies_list[proxy]["password"]
            self.type = proxies_list[proxy]["type"]
            self.ssh_command = proxies_list[proxy]["ssh_command"]


class params:
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
            c = credential(d.credential)
            attr = {
                "host": self.router,
                "device_type": self.type,
                "username": c.username,
                "password": c.password,
                "global_delay_factor": 0.5,
            }
            return attr

        def nm_proxy(self):
            p = proxy(d.proxy)
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
            c = credential(d.credential)
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
            dp = proxy(d.proxy)

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
                code = 415
                logger.error(f"{msg}, {code}, {lg_params}")
                raise
                return (general_error, code, lg_params)


def execute(lg_data):
    logger.info(f"Received lookup request for: {lg_data}")
    # Create individual variables for POSTed JSON from main app
    global lg_router
    lg_router = lg_data["router"]

    global lg_cmd
    lg_cmd = lg_data["cmd"]

    global lg_ipprefix
    lg_ipprefix = lg_data["ipprefix"]

    global lg_params
    lg_params = lg_data

    # Check blacklist.toml array for prefixes/IPs and return an error upon a match
    if lg_cmd in ["bgp_route", "ping", "traceroute"]:
        try:
            if IPNetwork(lg_ipprefix).ip in blacklist:
                msg = f"{lg_ipprefix} is not allowed."
                code = 405
                logger.error(f"{msg}, {code}, {lg_data}")
                return (msg, code, lg_data)
        # If netaddr library throws an exception, return a user-facing error.
        except:
            msg = f"{lg_ipprefix} is not a valid IP Address."
            code = 405
            logger.error(f"{msg}, {code}, {lg_data}")
            return (msg, code, lg_data)
    elif lg_cmd == "Query Type":
        msg = "You must select a query type."
        code = 405
        logger.error(f"{msg}, {code}, {lg_data}")
        return (msg, code, lg_data)

    global d
    d = device(lg_router)

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
                logger.error(general_error, 500, http())
                return general_error, 500, http()
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
                logger.error(general_error, 500, ssh())
                return general_error, 500, ssh()
        except:
            raise
