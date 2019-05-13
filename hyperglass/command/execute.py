#!/usr/bin/env python3

import sys
import time
from netaddr import *
from logzero import logger
from netmiko import redispatch
from netmiko import ConnectHandler
from hyperglass import configuration
from hyperglass.command import construct
from hyperglass.command import parse

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


def execute(lg_data):
    logger.info(f"Received lookup request for: {lg_data}")
    # Check POST data from JS, if location matches a configured router's
    # location, use the router's configured IP address to connect
    router = lg_data["router"]
    cmd = lg_data["cmd"]
    ipprefix = lg_data["ipprefix"]

    for r in routers_list:
        if r["location"] == router:
            lg_router_address = r["address"]

    # Check blacklist.toml array for prefixes/IPs and return an error upon a match
    if cmd in ["bgp_route", "ping", "traceroute"]:
        try:
            if IPNetwork(ipprefix).ip in blacklist:
                msg = f"{ipprefix} is not allowed."
                code = 405
                logger.error(f"{msg}, {code}, {lg_data}")
                return (msg, code, lg_data)
        # If netaddr library throws an exception, return a user-facing error.
        except:
            msg = f"{ipprefix} is not a valid IP Address."
            code = 415
            logger.error(f"{msg}, {code}, {lg_data}")
            return (msg, code, lg_data)
    # Send "clean" request to constructor to build the command that will be sent to the router
    msg, status, router, type, command = construct.construct(
        lg_router_address, cmd, ipprefix
    )
    # Loop through proxy config, match configured proxy name for each router with a configured proxy
    # Return configured proxy parameters for netmiko
    def matchProxy(search_proxy):
        if configured_proxy in proxies_list:
            proxy_address = proxies_list[search_proxy]["address"]
            proxy_username = proxies_list[search_proxy]["username"]
            proxy_password = proxies_list[search_proxy]["password"]
            proxy_type = proxies_list[search_proxy]["type"]
            proxy_ssh_command = proxies_list[search_proxy]["ssh_command"]
            return (
                proxy_address,
                proxy_username,
                proxy_password,
                proxy_type,
                proxy_ssh_command,
            )
        else:
            msg = "Router does not have a proxy configured."
            code = 415
            logger.error(f"{msg}, {code}, {lg_data}")
            return (msg, code, lg_data)

    # Matches router with configured credential
    def findCred(router):
        for r in routers_list:
            if r["address"] == router:
                configured_credential = r["credential"]
                return configured_credential

    # Matches configured credential with real username/password
    def returnCred(configured_credential):
        if configured_credential in credentials_list:
            matched_username = credentials_list[configured_credential]["username"]
            matched_password = credentials_list[configured_credential]["password"]
            return matched_username, matched_password
        else:
            msg = f"Credential {configured_credential} does not exist"
            code = 415
            logger.error(f"{msg}, {code}, {lg_data}")
            return (general_error, code, lg_data)

    # Connect to the router via netmiko library, return the command output
    def getOutputDirect():
        try:
            nm_connect_direct = ConnectHandler(**nm_host)
            nm_output_direct = nm_connect_direct.send_command(command)
            return nm_output_direct
        except:
            msg = f"Unable to reach target {router}"
            code = 415
            logger.error(f"{msg}, {code}, {lg_data}")
            return (general_error, code, lg_data)

    # Connect to the proxy server via netmiko library, then log into the router
    # via standard SSH
    def getOutputProxy(router_proxy):
        nm_proxy = {
            "host": matchProxy(router_proxy)[0],
            "username": matchProxy(router_proxy)[1],
            "password": matchProxy(router_proxy)[2],
            "device_type": matchProxy(router_proxy)[3],
        }
        nm_connect_proxied = ConnectHandler(**nm_proxy)
        nm_ssh_command = matchProxy(router_proxy)[4].format(**nm_host) + "\n"
        nm_connect_proxied.write_channel(nm_ssh_command)
        time.sleep(1)
        proxy_output = nm_connect_proxied.read_channel()
        try:
            # Accept SSH key warnings
            if "Are you sure you want to continue connecting" in proxy_output:
                nm_connect_proxied.write_channel("yes" + "\n")
                time.sleep(1)
                nm_connect_proxied.write_channel(nm_host["password"] + "\n")
            # Send password on prompt
            elif "assword" in proxy_output:
                nm_connect_proxied.write_channel(nm_host["password"] + "\n")
                time.sleep(1)
                proxy_output += nm_connect_proxied.read_channel()
            # Reclassify netmiko connection as configured device type
            redispatch(nm_connect_proxied, nm_host["device_type"])

            host_output = nm_connect_proxied.send_command(command)
            if host_output:
                return host_output
        except:
            msg = f'Proxy server {nm_proxy["host"]} unable to reach target {nm_host["host"]}'
            code = 415
            logger.error(f"{msg}, {code}, {lg_data}")
            return (general_error, code, lg_data)

    nm_host = {
        "host": router,
        "device_type": type,
        "username": returnCred(findCred(router))[0],
        "password": returnCred(findCred(router))[1],
    }

    # Loop through router list, determine if proxy exists
    for r in routers_list:
        if r["address"] == router:
            configured_proxy = r["proxy"]
            if len(configured_proxy) == 0:
                connection_proxied = False
            else:
                connection_proxied = True
    if status == 200:
        logger.info(f"Executing {command} on {router}...")
        try:
            if connection_proxied is True:
                output_proxied = getOutputProxy(configured_proxy)
                parsed_output = parse.parse(output_proxied, type, cmd)
                return parsed_output, status, router, type, command
            elif connection_proxied is False:
                output_direct = getOutputDirect()
                parsed_output = parse.parse(output_direct, type, cmd)
                return parsed_output, status, router, type, command
        except:
            raise
    else:
        return msg, status, router, type, command
