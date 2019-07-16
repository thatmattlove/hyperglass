#!/usr/bin/env python3
"""
Runs tests against test hyperglass instance
"""
import asyncio
import os
import json
import http3
import logzero

working_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(working_directory)

# Async loop
loop = asyncio.get_event_loop()

# Logzero Configuration
logger = logzero.logger
log_level = 10
log_format = (
    "%(color)s[%(module)s:%(funcName)s:%(lineno)d "
    "%(levelname)s]%(end_color)s %(message)s"
)
date_format = "%Y-%m-%d %H:%M:%S"
logzero_formatter = logzero.LogFormatter(fmt=log_format, datefmt=date_format)
logzero_config = logzero.setup_default_logger(
    formatter=logzero_formatter, level=log_level
)


async def ci_hyperglass_test(
    location, target_ipv4, target_ipv6, requires_ipv6_cidr, test_blacklist
):
    """
    Tests hyperglass backend by making use of HTTP3 library to mimic
    the JS Ajax POST performed by the front end.
    """
    invalid_ip = "this_ain't_an_ip!"
    invalid_aspath = ".*"
    ipv4_cidr = "1.1.1.0/24"
    ipv6_host = "2606:4700:4700::1111"
    ipv6_cidr = "2606:4700:4700::/48"
    test_headers = {"Content-Type": "application/json"}
    test_endpoint = "http://localhost:5000/lg"
    http_client = http3.AsyncClient()
    # No Query Type Test
    try:
        logger.info("Starting No Query Type test...")
        test_query = {"type": "", "location": location, "target": target_ipv4}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("No Query Type test failed")
    except:
        logger.error("Exception occurred while running No Query Type test...")
        raise
    # No Location Test
    try:
        logger.info("Starting No Location test...")
        test_query = {"type": "bgp_route", "location": "", "target": target_ipv6}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("No Location test failed")
    except:
        logger.error("Exception occurred while running No Location test...")
        raise
    # No Target Test
    try:
        logger.info("Starting No Target test...")
        test_query = {"type": "bgp_route", "location": location, "target": ""}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("No Target test failed")
    except:
        logger.error("Exception occurred while running No Target test...")
        raise
    # Invalid BGP Route Test
    try:
        logger.info("Starting Invalid BGP IPv4 Route test...")
        test_query = {"type": "bgp_route", "location": location, "target": invalid_ip}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Invalid BGP IPv4 Route test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP IPv4 Route test...")
    # Requires IPv6 CIDR Test
    if requires_ipv6_cidr:
        try:
            logger.info("Starting Requires IPv6 CIDR test...")
            test_query = {
                "type": "bgp_route",
                "location": requires_ipv6_cidr,
                "target": ipv6_host,
            }
            hg_response = await http_client.post(
                test_endpoint, headers=test_headers, json=test_query
            )
            if hg_response.status_code not in range(400, 500):
                logger.error(hg_response.text)
                raise RuntimeError("Requires IPv6 CIDR test failed")
        except:
            logger.error("Exception occurred while running Requires IPv6 CIDR test...")
            raise
    # Invalid BGP Community Test
    try:
        logger.info("Starting Invalid BGP Community test...")
        test_query = {
            "type": "bgp_community",
            "location": location,
            "target": target_ipv4,
        }
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Invalid BGP Community test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP Community test...")
        raise
    # Invalid BGP AS_PATH Test
    try:
        logger.info("Starting invalid BGP AS_PATH test...")
        test_query = {
            "type": "bgp_aspath",
            "location": location,
            "target": invalid_aspath,
        }
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Invalid BGP AS_PATH test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP AS_PATH test...")
        raise
    # Invalid IPv4 Ping Test
    try:
        logger.info("Starting Invalid IPv4 Ping test...")
        test_query = {"target": "ping", "location": location, "target": ipv4_cidr}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Invalid IPv4 Ping test failed")
    except:
        logger.error("Exception occurred while running Invalid IPv4 Ping test...")
        raise
    # Invalid IPv6 Ping Test
    try:
        logger.info("Starting Invalid IPv6 Ping test...")
        test_query = {"type": "ping", "location": location, "target": ipv6_cidr}
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Invalid IPv6 Ping test failed")
    except:
        logger.error("Exception occurred while running Invalid IPv6 Ping test...")
        raise
    # Blacklist Test
    try:
        logger.info("Starting Blacklist test...")
        test_query = {
            "type": "bgp_route",
            "location": location,
            "target": test_blacklist,
        }
        hg_response = await http_client.post(
            test_endpoint, headers=test_headers, json=test_query
        )
        if hg_response.status_code not in range(400, 500):
            logger.error(hg_response.text)
            raise RuntimeError("Blacklist test failed")
    except:
        logger.error("Exception occurred while running Blacklist test...")
        raise


if __name__ == "__main__":
    loop.run_until_complete(
        ci_hyperglass_test(
            "pop2", "1.1.1.0/24", "2606:4700:4700::/48", "pop1", "100.64.0.1"
        )
    )
