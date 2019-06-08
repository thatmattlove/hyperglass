# https://github.com/checktheroads/hyperglass
"""
Accepts input from front end application, validates the input and returns errors if input is \
invalid. Passes validated parameters to construct.py, which is used to build & run the Netmiko \
connectoins or hyperglass-frr API calls, returns the output back to the front end.
"""
# Module Imports
import json
import time
import requests
import requests.exceptions
from logzero import logger
from netmiko import (
    ConnectHandler,
    redispatch,
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
    NetmikoAuthError,
    NetmikoTimeoutError,
)

# Project Imports
from hyperglass import configuration
from hyperglass.command.construct import Construct
from hyperglass.command.validate import Validate

codes = configuration.codes()
config = configuration.general()


class Rest:
    """Executes connections to REST API devices"""

    # pylint: disable=too-few-public-methods
    # Dear PyLint, sometimes, people need to make their code scalable for future use. <3, -ML

    def __init__(self, transport, device, cmd, target):
        self.transport = transport
        self.device = device
        self.cmd = cmd
        self.target = target
        self.cred = configuration.credential(self.device["credential"])
        self.query = getattr(Construct(self.device), self.cmd)(
            self.transport, self.target
        )

    def frr(self):
        """Sends HTTP POST to router running the hyperglass-frr API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.cred["password"],
            }
            json_query = json.dumps(self.query)
            frr_endpoint = f'http://{self.device["address"]}:{self.device["port"]}/frr'
            frr_response = requests.post(frr_endpoint, headers=headers, data=json_query)
            response = frr_response.text
            status = frr_response.status_code
        except requests.exceptions.RequestException as requests_exception:
            logger.error(
                f'Error connecting to device {self.device["name"]}: {requests_exception}'
            )
            response = config["msg_error_general"]
            status = codes["danger"]
        return response, status


class Netmiko:
    """Executes connections to Netmiko devices"""

    # pylint: disable=too-many-instance-attributes
    # Dear PyLint, I actually need all these. <3, -ML

    def __init__(self, transport, device, cmd, target):
        self.device = device
        self.target = target
        self.cred = configuration.credential(self.device["credential"])
        self.params = getattr(Construct(device), cmd)(transport, target)
        self.router = self.params[0]
        self.nos = self.params[1]
        self.command = self.params[2]
        self.nm_host = {
            "host": self.router,
            "device_type": self.nos,
            "username": self.cred["username"],
            "password": self.cred["password"],
            "global_delay_factor": 0.5,
        }

    def direct(self):
        """Connects to the router via netmiko library, return the command output"""
        try:
            nm_connect_direct = ConnectHandler(**self.nm_host)
            response = nm_connect_direct.send_command(self.command)
            status = codes["success"]
        except (
            NetMikoAuthenticationException,
            NetMikoTimeoutException,
            NetmikoAuthError,
            NetmikoTimeoutError,
        ) as netmiko_exception:
            response = config["msg_error_general"]
            status = codes["danger"]
            logger.error(f"{netmiko_exception}, {status}")
        return response, status

    def proxied(self):
        """
        Connects to the proxy server via netmiko library, then logs into the router via \
        standard SSH
        """
        proxy_name = self.device["proxy"]
        device_proxy = configuration.proxy(proxy_name)
        nm_proxy = {
            "host": device_proxy["address"],
            "username": device_proxy["username"],
            "password": device_proxy["password"],
            "device_type": device_proxy["type"],
            "global_delay_factor": 0.5,
        }
        nm_connect_proxied = ConnectHandler(**nm_proxy)
        nm_ssh_command = device_proxy["ssh_command"].format(**self.nm_host) + "\n"
        nm_connect_proxied.write_channel(nm_ssh_command)
        time.sleep(1)
        proxy_output = nm_connect_proxied.read_channel()
        try:
            # Accept SSH key warnings
            if "Are you sure you want to continue connecting" in proxy_output:
                nm_connect_proxied.write_channel("yes" + "\n")
                nm_connect_proxied.write_channel(self.nm_host["password"] + "\n")
            # Send password on prompt
            elif "assword" in proxy_output:
                nm_connect_proxied.write_channel(self.nm_host["password"] + "\n")
                proxy_output += nm_connect_proxied.read_channel()
            # Reclassify netmiko connection as configured device type
            redispatch(nm_connect_proxied, self.nm_host["device_type"])
            response = nm_connect_proxied.send_command(self.command)
            status = codes["success"]
        except (
            NetMikoAuthenticationException,
            NetMikoTimeoutException,
            NetmikoAuthError,
            NetmikoTimeoutError,
        ) as netmiko_exception:
            response = config["msg_error_general"]
            status = codes["danger"]
            logger.error(
                f'{netmiko_exception}, {status},Proxy: {self.nm_host["proxy"]}'
            )
        return response, status


class Execute:
    """
    Ingests user input, runs blacklist check, runs prefix length check (if enabled), pulls all \
    configuraiton variables for the input router.
    """

    def __init__(self, lg_data):
        self.input_data = lg_data
        self.input_router = lg_data["router"]
        self.input_cmd = lg_data["cmd"]
        self.input_target = lg_data["ipprefix"]
        self.device_config = configuration.device(self.input_router)

    def parse(self, output):
        """Splits BGP output by AFI, returns only IPv4 & IPv6 output for protocol-agnostic \
        commands (Community & AS_PATH Lookups)"""
        nos = self.device_config["type"]
        parsed = output
        if self.input_cmd in ["bgp_community", "bgp_aspath"]:
            if nos in ["cisco_ios"]:
                delimiter = "For address family: "
                parsed_ipv4 = output.split(delimiter)[1]
                parsed_ipv6 = output.split(delimiter)[2]
                parsed = delimiter + parsed_ipv4 + delimiter + parsed_ipv6
            if nos in ["cisco_xr"]:
                delimiter = "Address Family: "
                parsed_ipv4 = output.split(delimiter)[1]
                parsed_ipv6 = output.split(delimiter)[2]
                parsed = delimiter + parsed_ipv4 + delimiter + parsed_ipv6
        return parsed

    def response(self):
        """
        Initializes Execute.filter(), if input fails to pass filter, returns errors to front end. \
        Otherwise, executes queries.
        """
        # Return error if no query type is specified
        if self.input_cmd == "Query Type":
            msg = config["msg_error_querytype"]
            status = codes["warning"]
            return msg, status, self.input_data
        validity, msg, status = getattr(Validate(self.device_config), self.input_cmd)(
            self.input_target
        )
        if not validity:
            return msg, status, self.input_data
        connection = None
        output = config["msg_error_general"]
        info = self.input_data
        if self.device_config["type"] == "frr":
            connection = Rest(
                "rest", self.device_config, self.input_cmd, self.input_target
            )
            raw_output, status = connection.frr()
            output = self.parse(raw_output)
        if self.device_config["type"] in configuration.scrape_list():
            connection = Netmiko(
                "scrape", self.device_config, self.input_cmd, self.input_target
            )
            if self.device_config["proxy"]:
                raw_output, status = connection.proxied()
            else:
                raw_output, status = connection.direct()
            output = self.parse(raw_output)
        else:
            logger.error(f"{output}, {status}, {info}")
        return output, status, info
