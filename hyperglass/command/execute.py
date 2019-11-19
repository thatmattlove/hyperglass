# https://github.com/checktheroads/hyperglass
"""
Accepts input from front end application, validates the input and returns errors if input is \
invalid. Passes validated parameters to construct.py, which is used to build & run the Netmiko \
connectoins or hyperglass-frr API calls, returns the output back to the front end.
"""
# Standard Imports
import json
import time
import logging

# Module Imports
import requests
import requests.exceptions
from logzero import logger
import logzero
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
config = configuration.params()
# config = configuration.general()

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)


class Rest:
    """Executes connections to REST API devices"""

    # pylint: disable=too-few-public-methods
    # Dear PyLint, sometimes, people need to make their code scalable for future use. <3, -ML

    def __init__(self, transport, device, query_type, target):
        self.transport = transport
        self.device = device
        self.query_type = query_type
        self.target = target
        self.cred = configuration.credential(self.device["credential"])
        self.query = getattr(Construct(self.device), self.query_type)(
            self.transport, self.target
        )

    def frr(self):
        """Sends HTTP POST to router running the hyperglass-frr API"""
        # Debug
        logger.debug(f"FRR host params:\n{self.device}")
        logger.debug(f"Raw query parameters: {self.query}")
        # End Debug
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.cred["password"],
            }
            json_query = json.dumps(self.query)
            frr_endpoint = f'http://{self.device["address"]}:{self.device["port"]}/frr'
            # Debug
            logger.debug(f"HTTP Headers:\n{headers}")
            logger.debug(f"JSON query:\n{json_query}")
            logger.debug(f"FRR endpoint: {frr_endpoint}")
            # End Debug
            frr_response = requests.post(
                frr_endpoint, headers=headers, data=json_query, timeout=7
            )
            response = frr_response.text
            status = frr_response.status_code
            # Debug
            logger.debug(f"FRR response text:\n{response}")
            logger.debug(f"FRR status code: {status}")
            # End Debug
        except requests.exceptions.RequestException as requests_exception:
            logger.error(
                f"Error connecting to device {self.device}: {requests_exception}"
            )
            response = config["messages"]["general"]
            status = codes["danger"]
        return response, status

    def bird(self):
        """Sends HTTP POST to router running the hyperglass-bird API"""
        # Debug
        logger.debug(f"BIRD host params:\n{self.device}")
        logger.debug(f"Raw query parameters: {self.query}")
        # End Debug
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.cred["password"],
            }
            json_query = json.dumps(self.query)
            bird_endpoint = (
                f'http://{self.device["address"]}:{self.device["port"]}/bird'
            )
            # Debug
            logger.debug(f"HTTP Headers:\n{headers}")
            logger.debug(f"JSON query:\n{json_query}")
            logger.debug(f"BIRD endpoint: {bird_endpoint}")
            # End Debug
            bird_response = requests.post(
                bird_endpoint, headers=headers, data=json_query, timeout=7
            )
            response = bird_response.text
            status = bird_response.status_code
            # Debug
            logger.debug(f"BIRD response text:\n{response}")
            logger.debug(f"BIRD status code: {status}")
            # End Debug
        except requests.exceptions.RequestException as requests_exception:
            logger.error(
                f"Error connecting to device {self.device}: {requests_exception}"
            )
            response = config["messages"]["general"]
            status = codes["danger"]
        return response, status


class Netmiko:
    """Executes connections to Netmiko devices"""

    # pylint: disable=too-many-instance-attributes
    # Dear PyLint, I actually need all these. <3, -ML

    def __init__(self, transport, device, query_type, target):
        self.device = device
        self.target = target
        self.cred = configuration.credential(self.device["credential"])
        self.params = getattr(Construct(device), query_type)(transport, target)
        self.location = self.params[0]
        self.nos = self.params[1]
        self.command = self.params[2]
        self.nm_host = {
            "host": self.location,
            "device_type": self.nos,
            "username": self.cred["username"],
            "password": self.cred["password"],
            "global_delay_factor": 0.5,
        }

    def direct(self):
        """Connects to the router via netmiko library, return the command output"""
        # Debug
        logger.debug(f"Netmiko host: {self.nm_host}")
        logger.debug(f"Connecting to host via Netmiko library...")
        # End Debug
        try:
            nm_connect_direct = ConnectHandler(**self.nm_host)
            response = nm_connect_direct.send_command(self.command)
            status = codes["success"]
            logger.debug(
                f"Response for direction connection with command {self.command}:\n{response}"
            )
        except (
            NetMikoAuthenticationException,
            NetMikoTimeoutException,
            NetmikoAuthError,
            NetmikoTimeoutError,
        ) as netmiko_exception:
            response = config["messages"]["general"]
            status = codes["danger"]
            logger.error(f"{netmiko_exception}, {status}")
        nm_connect_direct.disconnect()
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
        # Debug
        logger.debug(f"Netmiko proxy {proxy_name}:\n{nm_proxy}")
        logger.debug(f"Proxy SSH command: {nm_ssh_command}")
        # End Debug
        nm_connect_proxied.write_channel(nm_ssh_command)
        time.sleep(1)
        proxy_output = nm_connect_proxied.read_channel()
        logger.debug(f"Proxy output:\n{proxy_output}")
        try:
            # Accept SSH key warnings
            if "Are you sure you want to continue connecting" in proxy_output:
                logger.debug(f"Received OpenSSH key warning")
                nm_connect_proxied.write_channel("yes" + "\n")
                nm_connect_proxied.write_channel(self.nm_host["password"] + "\n")
            # Send password on prompt
            elif "assword" in proxy_output:
                logger.debug(f"Received password prompt")
                nm_connect_proxied.write_channel(self.nm_host["password"] + "\n")
                proxy_output += nm_connect_proxied.read_channel()
            # Reclassify netmiko connection as configured device type
            logger.debug(
                f'Redispatching netmiko with device class {self.nm_host["device_type"]}'
            )
            redispatch(nm_connect_proxied, self.nm_host["device_type"])
            response = nm_connect_proxied.send_command(self.command)
            status = codes["success"]
            logger.debug(f"Netmiko proxied response:\n{response}")
        except (
            NetMikoAuthenticationException,
            NetMikoTimeoutException,
            NetmikoAuthError,
            NetmikoTimeoutError,
        ) as netmiko_exception:
            response = config["messages"]["general"]
            status = codes["danger"]
            logger.error(
                f'{netmiko_exception}, {status},Proxy: {self.nm_host["proxy"]}'
            )
        nm_connect_proxied.disconnect()
        return response, status


class Execute:
    """
    Ingests user input, runs blacklist check, runs prefix length check (if enabled), pulls all \
    configuraiton variables for the input router.
    """

    def __init__(self, lg_data):
        self.input_data = lg_data
        self.input_location = self.input_data["location"]
        self.input_type = self.input_data["type"]
        self.input_target = self.input_data["target"]

    def parse(self, output, nos):
        """Splits BGP output by AFI, returns only IPv4 & IPv6 output for protocol-agnostic \
        commands (Community & AS_PATH Lookups)"""
        logger.debug(f"Parsing output...")
        parsed = output
        if self.input_type in ["bgp_community", "bgp_aspath"]:
            if nos in ["cisco_ios"]:
                logger.debug(f"Parsing output for device type {nos}")
                delimiter = "For address family: "
                parsed_ipv4 = output.split(delimiter)[1]
                parsed_ipv6 = output.split(delimiter)[2]
                parsed = delimiter + parsed_ipv4 + delimiter + parsed_ipv6
            if nos in ["cisco_xr"]:
                logger.debug(f"Parsing output for device type {nos}")
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
        device_config = configuration.device(self.input_location)
        # Debug
        logger.debug(f"Received query for {self.input_data}")
        logger.debug(f"Matched device config:\n{device_config}")
        # End Debug
        validity, msg, status = getattr(Validate(device_config), self.input_type)(
            self.input_target
        )
        if not validity:
            logger.debug(f"Invalid query")
            ## return msg, status, self.input_data
            return {"output": msg, "status": status}
        connection = None
        output = config["messages"]["general"]
        info = self.input_data
        logger.debug(f"Validity: {validity}, Message: {msg}, Status: {status}")
        if device_config["type"] in configuration.rest_list():
            connection = Rest("rest", device_config, self.input_type, self.input_target)
            raw_output, status = getattr(connection, device_config["type"])()
            output = self.parse(raw_output, device_config["type"])
            ## return output, status, info
            return {"output": output, "status": status}
        if device_config["type"] in configuration.scrape_list():
            logger.debug(f"Initializing Netmiko...")
            connection = Netmiko(
                "scrape", device_config, self.input_type, self.input_target
            )
            if device_config["proxy"]:
                raw_output, status = connection.proxied()
            else:
                raw_output, status = connection.direct()
            output = self.parse(raw_output, device_config["type"])
            logger.debug(
                f'Parsed output for device type {device_config["type"]}:\n{output}'
            )
            ## return output, status, info
            return {"output": output, "status": status}
        if device_config["type"] not in configuration.supported_nos():
            logger.error(
                f"Device not supported, or no commands for device configured. {status}, {info}"
            )
        ## return output, status, info
        return {"output": output, "status": status}
