#!/usr/bin/env python3
"""
Runs tests against test hyperglass instance
"""
import os
import json
import requests
from logzero import logger

working_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(working_directory)


def construct_test(test_query, location, test_target):
    """Constructs JSON POST data for test_hyperglass function"""
    constructed_query = json.dumps(
        {"type": test_query, "location": location, "target": test_target}
    )
    return constructed_query


def ci_hyperglass_test(
    location,
    target_ipv4,
    target_ipv6,
    requires_ipv6_cidr,
    test_blacklist,
    test_host,
    test_port,
):
    """Tests hyperglass backend by making use of requests library to mimic the JS Ajax POST \
    performed by the front end."""
    invalid_ip = "this_ain't_an_ip!"
    invalid_aspath = ".*"
    ipv4_cidr = "1.1.1.0/24"
    ipv6_host = "2606:4700:4700::1111"
    ipv6_cidr = "2606:4700:4700::/48"
    test_headers = {"Content-Type": "application/json"}
    test_endpoint = f"http://{test_host}:{test_port}/lg"
    # No Query Type Test
    try:
        logger.info("Starting No Query Type test...")
        test_query = construct_test("", location, target_ipv4)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("No Query Type test failed")
    except:
        logger.error("Exception occurred while running No Query Type test...")
        raise
    # No Location Test
    try:
        logger.info("Starting No Location test...")
        test_query = construct_test("bgp_route", "", target_ipv6)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("No Location test failed")
    except:
        logger.error("Exception occurred while running No Location test...")
        raise
    # No Target Test
    try:
        logger.info("Starting No Target test...")
        test_query = construct_test("bgp_route", location, "")
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("No Target test failed")
    except:
        logger.error("Exception occurred while running No Target test...")
        raise
    # Invalid BGP Route Test
    try:
        logger.info("Starting Invalid BGP IPv4 Route test...")
        test_query = construct_test("bgp_route", location, invalid_ip)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Invalid BGP IPv4 Route test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP IPv4 Route test...")
    # Requires IPv6 CIDR Test
    if requires_ipv6_cidr:
        try:
            logger.info("Starting Requires IPv6 CIDR test...")
            test_query = construct_test("bgp_route", requires_ipv6_cidr, ipv6_host)
            hg_response = requests.post(
                test_endpoint, headers=test_headers, data=test_query
            )
            if not hg_response.status_code in range(400, 500):
                raise RuntimeError("Requires IPv6 CIDR test failed")
        except:
            logger.error("Exception occurred while running Requires IPv6 CIDR test...")
            raise
    # Invalid BGP Community Test
    try:
        logger.info("Starting Invalid BGP Community test...")
        test_query = construct_test("bgp_community", location, target_ipv4)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Invalid BGP Community test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP Community test...")
        raise
    # Invalid BGP AS_PATH Test
    try:
        logger.info("Starting invalid BGP AS_PATH test...")
        test_query = construct_test("bgp_aspath", location, invalid_aspath)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Invalid BGP AS_PATH test failed")
    except:
        logger.error("Exception occurred while running Invalid BGP AS_PATH test...")
        raise
    # Invalid IPv4 Ping Test
    try:
        logger.info("Starting Invalid IPv4 Ping test...")
        test_query = construct_test("ping", location, ipv4_cidr)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Invalid IPv4 Ping test failed")
    except:
        logger.error("Exception occurred while running Invalid IPv4 Ping test...")
        raise
    # Invalid IPv6 Ping Test
    try:
        logger.info("Starting Invalid IPv6 Ping test...")
        test_query = construct_test("ping", location, ipv6_cidr)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Invalid IPv6 Ping test failed")
    except:
        logger.error("Exception occurred while running Invalid IPv6 Ping test...")
        raise
    # Blacklist Test
    try:
        logger.info("Starting Blacklist test...")
        test_query = construct_test("bgp_route", location, test_blacklist)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if not hg_response.status_code in range(400, 500):
            raise RuntimeError("Blacklist test failed")
    except:
        logger.error("Exception occurred while running Blacklist test...")
        raise


if __name__ == "__main__":
    ci_hyperglass_test(
        "pop2",
        "1.1.1.0/24",
        "2606:4700:4700::/48",
        "pop1",
        "100.64.0.1",
        "localhost",
        5000,
    )
