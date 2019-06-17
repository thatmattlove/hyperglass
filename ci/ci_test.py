import os
import sys
import glob
import shutil
import inspect
import requests
from logzero import logger

working_directory = os.path.dirname(os.path.abspath(__file__))


def ci_config():
    """Copies test configuration files to usable config files"""
    logger.info("Migrating test config files...")
    config_dir = os.path.join(working_directory, "hyperglass/configuration/")
    test_files = glob.iglob(os.path.join(working_directory, "*.toml"))
    logger.debug(config_dir)
    status = False
    for f in test_files:
        logger.debug(f)
        if os.path.exists(f):
            logger.debug(f"{f} already exists")
            raise RuntimeError(f"{f} already exists")
        else:
            try:
                shutil.copy(f, config_dir)
                logger.info("Successfully migrated test config files")
                status = True
                logger.debug(status)
                return status
            except:
                logger.error(f"Failed to migrate {f}")
                raise
    return status


def construct_test(test_query, location, test_target):
    """Constructs JSON POST data for test_hyperglass function"""
    constructed_query = json.dumps(
        {"type": test_query, "location": location, "target": test_target}
    )
    return constructed_query


def ci_test(
    location,
    target_ipv4,
    target_ipv6,
    requires_ipv6_cidr,
    test_blacklist,
    test_community,
    test_aspath,
    test_host,
    test_port,
):
    """Fully tests hyperglass backend by making use of requests library to mimic the JS Ajax POST \
    performed by the front end."""
    test_target = None
    invalid_ip = "this_ain't_an_ip!"
    invalid_community = "192.0.2.1"
    invalid_aspath = ".*"
    ipv4_host = "1.1.1.1"
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


def flask_dev_server(host, port):
    """Starts Flask development server for testing without WSGI/Reverse Proxy"""
    try:
        parent_directory = os.path.dirname(working_directory)
        sys.path.insert(0, parent_directory)

        from hyperglass import hyperglass
        from hyperglass import configuration
        from hyperglass import render

        render.css()
        logger.info("Starting Flask development server")
        hyperglass.app.run(host=host, debug=True, port=port)
    except:
        logger.error("Exception occurred while trying to start test server...")
        raise


def ci_test():
    if ci_config():
        flask_dev_server("localhost", 5000)
        ci_test(
            "pop2",
            "1.1.1.0/24",
            "2606:4700:4700::/48",
            "pop1",
            "100.64.0.1",
            "65001:1",
            "_65001$",
            "localhost",
            5000,
        )
    else:
        raise


if __name__ == "__main__":
    ci_test()
