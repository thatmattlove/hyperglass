#!/usr/bin/env python3

# Standard Imports
import os
import grp
import pwd
import sys
import glob
import random
import shutil
import string

# Module Imports
import click
import json
from passlib.hash import pbkdf2_sha256
import requests

# Initialize shutil copy function
cp = shutil.copyfile


def construct_test(test_query, location, test_target):
    """Constructs JSON POST data for test_hyperglass function"""
    constructed_query = json.dumps(
        {"type": test_query, "location": location, "target": test_target}
    )
    return constructed_query


@click.group()
def hg():
    pass


@hg.command("pre-check", help="Check hyperglass config & readiness")
def pre_check():
    if sys.version_info < (3, 6):
        click.secho(
            f"Hyperglass requires Python 3.6 or higher. Curren version: Python {sys.version.split()[0]}",
            fg="red",
            bold=True,
        )
    if sys.version_info >= (3, 6):
        click.secho(
            f"✓ Python Version Check passed (Current version: Python {sys.version.split()[0]})",
            fg="green",
            bold=True,
        )
    try:
        from hyperglass import configuration

        config = configuration.params()
        status = True
        while status:
            if config["general"]["primary_asn"] == "65000" or "":
                status = False
                reason = f'Primary ASN is not defined (Current: "{config["general"]["primary_asn"]}")'
                remediation = f"""
To define the Primary ASN paramter, modify your `configuration.toml` and add the following \
configuration:\n
[general]
primary_asn = "<Your Primary AS Number>"
\nIf you do not define a Primary ASN, \"{config["general"]["primary_asn"]}\" will be used."""
                break
                click.secho(reason, fg="red", bold=True)
                click.secho(remediation, fg="blue")
            if config["general"]["org_name"] == "The Company" or "":
                status = False
                reason = f'Org Name is not defined (Current: "{config["general"]["org_name"]}")'
                remediation = f"""
To define an Org Name paramter, modify your `configuration.toml` and add the following \
configuration:\n
[general]
org_name = "<Your Org Name>"
\nIf you do not define an Org Name, \"{config["general"]["org_name"]}\" will be displayed."""
                break
                click.secho(reason, fg="red", bold=True)
                click.secho(remediation, fg="blue")
        click.secho(
            "All critical hyperglass parameters are defined!", fg="green", bold=True
        )
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}", fg="red")


@hg.command("test", help="Full test of all backend features")
@click.option("-l", "--location", type=str, required=True, help="Location to query")
@click.option(
    "-4",
    "--target-ipv4",
    "target_ipv4",
    type=str,
    default="1.1.1.0/24",
    required=False,
    show_default=True,
    help="IPv4 Target Address",
)
@click.option(
    "-6",
    "--target-ipv6",
    "target_ipv6",
    type=str,
    default="2606:4700:4700::/48",
    required=False,
    show_default=True,
    help="IPv6 Target Address",
)
@click.option(
    "-c",
    "--community",
    "test_community",
    type=str,
    required=False,
    show_default=True,
    default="65000:1",
    help="BGP Community",
)
@click.option(
    "-a",
    "--aspath",
    "test_aspath",
    type=str,
    required=False,
    show_default=True,
    default="^65001$",
    help="BGP AS Path",
)
@click.option(
    "-r",
    "--requires-ipv6-cidr",
    "requires_ipv6_cidr",
    type=str,
    required=False,
    help="Location for testing IPv6 CIDR requirement",
)
@click.option(
    "-b",
    "--blacklist",
    "test_blacklist",
    type=str,
    default="100.64.0.1",
    required=False,
    show_default=True,
    help="Address to use for blacklist check",
)
@click.option(
    "-h",
    "--host",
    "test_host",
    type=str,
    default="localhost",
    required=False,
    show_default=True,
    help="Name or IP address of hyperglass server",
)
@click.option(
    "-p",
    "--port",
    "test_port",
    type=int,
    default=5000,
    required=False,
    show_default=True,
    help="Port hyperglass is running on",
)
def test_hyperglass(
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
        click.secho("Starting No Query Type test...", fg="black")
        test_query = construct_test("", location, target_ipv4)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ No Query Type test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ No Query Type test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # No Location Test
    try:
        click.secho("Starting No Location test...", fg="black")
        test_query = construct_test("bgp_route", "", target_ipv6)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ No Location test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ No Location test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # No Location Test
    try:
        click.secho("Starting No Target test...", fg="black")
        test_query = construct_test("bgp_route", location, "")
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ No Target test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ No Target test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Valid BGP IPv4 Route Test
    try:
        click.secho("Starting Valid BGP IPv4 Route test...", fg="black")
        test_query = construct_test("bgp_route", location, target_ipv4)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid BGP IPv4 Route test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid BGP IPv4 Route test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Valid BGP IPv6 Route Test
    try:
        click.secho("Starting Valid BGP IPv6 Route test...", fg="black")
        test_query = construct_test("bgp_route", location, target_ipv6)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid BGP IPv6 Route test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid BGP IPv6 Route test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Invalid BGP Route Test
    try:
        click.secho("Starting Invalid BGP IPv4 Route test...", fg="black")
        test_query = construct_test("bgp_route", location, invalid_ip)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Invalid BGP IPv4 Route test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Invalid BGP IPv4 Route test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Requires IPv6 CIDR Test
    if requires_ipv6_cidr:
        try:
            click.secho("Starting Requires IPv6 CIDR test...", fg="black")
            test_query = construct_test("bgp_route", requires_ipv6_cidr, ipv6_host)
            hg_response = requests.post(
                test_endpoint, headers=test_headers, data=test_query
            )
            if hg_response.status_code in range(400, 500):
                click.secho("✓ Requires IPv6 CIDR test passed", fg="green", bold=True)
            if not hg_response.status_code in range(400, 500):
                click.secho("✗ Requires IPv6 CIDR test failed", fg="red", bold=True)
                click.secho(
                    f"Status Code: {hg_response.status_code}", fg="red", bold=True
                )
                click.secho(hg_response.text, fg="red")
        except Exception as e:
            click.secho(f"Exception occurred:\n{e}")
    # Valid BGP Community Test
    try:
        click.secho("Starting Valid BGP Community test...", fg="black")
        test_query = construct_test("bgp_community", location, test_community)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid BGP Community test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid BGP Community test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Invalid BGP Community Test
    try:
        click.secho("Starting Invalid BGP Community test...", fg="black")
        test_query = construct_test("bgp_community", location, target_ipv4)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Invalid BGP Community test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Invalid BGP Community test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Valid BGP AS_PATH Test
    try:
        click.secho("Starting Valid BGP AS_PATH test...", fg="black")
        test_query = construct_test("bgp_aspath", location, test_aspath)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid BGP AS_PATH test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid BGP AS_PATH test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Invalid BGP AS_PATH Test
    try:
        click.secho("Starting invalid BGP AS_PATH test...", fg="black")
        test_query = construct_test("bgp_aspath", location, invalid_aspath)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Invalid BGP AS_PATH test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Invalid BGP AS_PATH test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Valid IPv4 Ping Test
    try:
        click.secho("Starting Valid IPv4 Ping test...", fg="black")
        test_query = construct_test("ping", location, ipv4_host)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid IPv4 Ping test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid IPv4 Ping test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Valid IPv6 Ping Test
    try:
        click.secho("Starting Valid IPv6 Ping test...", fg="black")
        test_query = construct_test("ping", location, ipv6_host)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code == 200:
            click.secho("✓ Valid IPv6 Ping test passed", fg="green", bold=True)
        if not hg_response.status_code == 200:
            click.secho("✗ Valid IPv6 Ping test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Invalid IPv4 Ping Test
    try:
        click.secho("Starting Invalid IPv4 Ping test...", fg="black")
        test_query = construct_test("ping", location, ipv4_cidr)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Invalid IPv4 Ping test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Invalid IPv4 Ping test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Invalid IPv6 Ping Test
    try:
        click.secho("Starting Invalid IPv6 Ping test...", fg="black")
        test_query = construct_test("ping", location, ipv6_cidr)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Invalid IPv6 Ping test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Invalid IPv6 Ping test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")
    # Blacklist Test
    try:
        click.secho("Starting Blacklist test...", fg="black")
        test_query = construct_test("bgp_route", location, test_blacklist)
        hg_response = requests.post(
            test_endpoint, headers=test_headers, data=test_query
        )
        if hg_response.status_code in range(400, 500):
            click.secho("✓ Blacklist test passed", fg="green", bold=True)
        if not hg_response.status_code in range(400, 500):
            click.secho("✗ Blacklist test failed", fg="red", bold=True)
            click.secho(f"Status Code: {hg_response.status_code}", fg="red", bold=True)
            click.secho(hg_response.text, fg="red")
    except Exception as e:
        click.secho(f"Exception occurred:\n{e}")


@hg.command("clear-cache", help="Clear Flask cache")
def clearcache():
    """Clears the Flask-Caching cache"""
    try:
        import hyperglass.hyperglass

        hyperglass.hyperglass.clear_cache()
        click.secho("✓ Successfully cleared cache.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to clear cache.", fg="red", bold=True)
        raise


@hg.command("generate-key", help="Generate API key & hash")
@click.option(
    "-l", "--length", "string_length", type=int, default=16, show_default=True
)
def generatekey(string_length):
    """Generates 16 character API Key for hyperglass-frr API, and a corresponding PBKDF2 SHA256 Hash"""
    ld = string.ascii_letters + string.digits
    api_key = "".join(random.choice(ld) for i in range(string_length))
    key_hash = pbkdf2_sha256.hash(api_key)
    click.secho(
        f"""
Your API Key is: {api_key}
Place your API Key in the `configuration.py` of your API module. For example, in: `hyperglass-frr/configuration.py`

Your Key Hash is: {key_hash}
Use this hash as the password for the device using the API module. For example, in: `hyperglass/hyperglass/configuration/devices.toml`
"""
    )


@hg.command("dev-server", help="Start Flask development server")
@click.option("--host", type=str, default="0.0.0.0", help="Listening IP")
@click.option("--port", type=int, default=5000, help="TCP Port")
def flask_dev_server(host, port):
    """Starts Flask development server for testing without WSGI/Reverse Proxy"""
    try:
        from hyperglass import hyperglass
        from hyperglass import configuration
        from hyperglass import render

        debug_state = configuration.debug_state()
        render.css()
        click.secho(f"✓ Starting Flask development server", fg="green", bold=True)
        hyperglass.app.run(host=host, debug=debug_state, port=port)
    except:
        click.secho("✗ Failed to start test server.", fg="red", bold=True)
        raise


@hg.command("compile-sass", help="Compile Sass templates to CSS")
def compile_sass():
    """Renders Jinja2 and Sass templates to HTML & CSS files"""
    try:
        from hyperglass import render

        render.css()
        click.secho("✓ Successfully rendered CSS templates.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to render CSS templates.", fg="red", bold=True)
        raise


@hg.command("migrate-configs", help="Copy TOML examples to usable config files")
def migrateconfig():
    """Copies example configuration files to usable config files"""
    try:
        click.secho("Migrating example config files...", fg="black")
        working_directory = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(working_directory, "hyperglass/configuration/")
        examples = glob.iglob(os.path.join(config_dir, "*.example"))
        for f in examples:
            basefile, extension = os.path.splitext(f)
            if os.path.exists(basefile):
                click.secho(f"{basefile} already exists", fg="blue")
            else:
                try:
                    cp(f, basefile)
                    click.secho(f"✓ Migrated {basefile}", fg="green")
                except:
                    click.secho(f"✗ Failed to migrate {basefile}", fg="red")
                    raise
        click.secho(
            "✓ Successfully migrated example config files", fg="green", bold=True
        )
    except:
        click.secho("✗ Error migrating example config files", fg="red", bold=True)
        raise


@hg.command("migrate-gunicorn", help="Copy Gunicorn example to usable config file")
def migrategunicorn():
    """Copies example Gunicorn config file to a usable config"""
    try:
        import hyperglass
    except ImportError as error_exception:
        click.secho(f"Error while importing hyperglass:\n{error_exception}", fg="red")
    try:
        click.secho("Migrating example Gunicorn configuration...", fg="black")
        hyperglass_root = os.path.dirname(hyperglass.__file__)
        ex_file = os.path.join(hyperglass_root, "gunicorn_config.py.example")
        basefile, extension = os.path.splitext(ex_file)
        newfile = basefile
        if os.path.exists(newfile):
            click.secho(f"{newfile} already exists", fg="blue")
        else:
            try:
                cp(ex_file, newfile)
                click.secho(
                    f"✓ Successfully migrated Gunicorn configuration to: {newfile}",
                    fg="green",
                    bold=True,
                )
            except:
                click.secho(f"✗ Failed to migrate {newfile}", fg="red")
                raise
    except:
        click.secho(
            "✗ Error migrating example Gunicorn configuration", fg="red", bold=True
        )
        raise


@hg.command("migrate-systemd", help="Copy Systemd example to OS")
@click.option(
    "-d", "--directory", default="/etc/systemd/system", help="Destination Directory"
)
def migratesystemd(directory):
    """Copies example systemd service file to /etc/systemd/system/"""
    try:
        click.secho("Migrating example systemd service...", fg="black")
        working_directory = os.path.dirname(os.path.abspath(__file__))
        ex_file_base = "hyperglass.service.example"
        ex_file = os.path.join(working_directory, f"hyperglass/{ex_file_base}")
        basefile, extension = os.path.splitext(ex_file_base)
        newfile = os.path.join(directory, basefile)
        if os.path.exists(newfile):
            click.secho(f"{newfile} already exists", fg="blue")
        else:
            try:
                cp(ex_file, newfile)
                click.secho(
                    f"✓ Successfully migrated systemd service to: {newfile}",
                    fg="green",
                    bold=True,
                )
            except:
                click.secho(f"✗ Failed to migrate {newfile}", fg="red")
                raise
    except:
        click.secho("✗ Error migrating example systemd service", fg="red", bold=True)
        raise


@hg.command(
    "update-permissions",
    help="Fix ownership & permissions of hyperglass project directory",
)
@click.option("--user", default="www-data")
@click.option("--group", default="www-data")
def fixpermissions(user, group):
    """Effectively runs `chmod` and `chown` on the hyperglass/hyperglass directory"""
    try:
        import hyperglass
    except ImportError as error_exception:
        click.secho(f"Error importing hyperglass:\n{error_exception}")
    hyperglass_root = os.path.dirname(hyperglass.__file__)
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    try:
        for root, dirs, files in os.walk(hyperglass_root):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chown(full_path, uid, gid)
            for f in files:
                full_path = os.path.join(root, f)
                os.chown(full_path, uid, gid)
            os.chown(root, uid, gid)
        click.secho(
            "✓ Successfully changed hyperglass/ ownership", fg="green", bold=True
        )
    except:
        click.secho("✗ Failed to change hyperglass/ ownership", fg="red", bold=True)
        raise
    try:
        for root, dirs, files in os.walk(hyperglass_root):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chmod(full_path, 0o744)
            for f in files:
                full_path = os.path.join(root, f)
                os.chmod(full_path, 0o744)
            os.chmod(root, 0o744)
        click.secho(
            "✓ Successfully changed hyperglass/ permissions", fg="green", bold=True
        )
    except:
        click.secho("✗ Failed to change hyperglass/ permissions", fg="red", bold=True)
        raise


if __name__ == "__main__":
    hg()
