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
from passlib.hash import pbkdf2_sha256

# Project Imports
from hyperglass import hyperglass
from hyperglass import render

# Initialize shutil copy function
cp = shutil.copyfile


@click.group()
def hg():
    pass


@hg.command()
def clearcache():
    """Clears the Flask-Caching cache"""
    try:
        hyperglass.clear_cache()
        click.secho("✓ Successfully cleared cache.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to clear cache.", fg="red", bold=True)
        raise


@hg.command()
def generatekey(string_length=16):
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


@hg.command()
def devserver():
    """Starts Flask development server for testing without WSGI/Reverse Proxy"""
    try:
        hyperglass.render.css()
        # hyperglass.metrics.start_http_server(9100)
        hyperglass.app.run(host="0.0.0.0", debug=True, port=5000)
        click.secho("✓ Started test server.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to start test server.", fg="red", bold=True)
        raise


@hg.command()
def render():
    """Renders Jinja2 and Sass templates to HTML & CSS files"""
    try:
        hyperglass.render.css()
        click.secho("✓ Successfully rendered CSS templates.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to render CSS templates.", fg="red", bold=True)
        raise


@hg.command()
def content():
    """Renders Jinja2 and Sass templates to HTML & CSS files"""
    try:
        hyperglass.render.markdown()
        click.secho("✓ Successfully rendered content templates.", fg="green", bold=True)
    except:
        click.secho("✗ Failed to render content templates.", fg="red", bold=True)
        raise


@hg.command()
def migrateconfig():
    """Copies example configuration files to usable config files"""
    try:
        click.secho("Migrating example config files...", fg="cyan")
        hyperglass_root = os.path.dirname(hyperglass.__file__)
        config_dir = os.path.join(hyperglass_root, "configuration/")
        examples = glob.iglob(os.path.join(config_dir, "*.example"))
        for f in examples:
            basefile, extension = os.path.splitext(f)
            newfile = basefile
            if os.path.exists(newfile):
                click.secho(f"{newfile} already exists", fg="blue")
            else:
                try:
                    cp(f, newfile)
                    click.secho(f"✓ Migrated {newfile}", fg="green")
                except:
                    click.secho(f"✗ Failed to migrate {newfile}", fg="red")
                    raise
        click.secho(
            "✓ Successfully migrated example config files", fg="green", bold=True
        )
    except:
        click.secho("✗ Error migrating example config files", fg="red", bold=True)
        raise


@hg.command()
def migrategunicorn():
    """Copies example Gunicorn config file to a usable config"""
    try:
        click.secho("Migrating example Gunicorn configuration...", fg="cyan")
        hyperglass_root = os.path.dirname(hyperglass.__file__)
        ex_file = os.path.join(hyperglass_root, "gunicorn_config.py.example")
        basefile, extension = os.path.splitext(ex_file)
        newfile = basefile
        if os.path.exists(newfile):
            click.secho(f"{newfile} already exists", fg="blue")
        else:
            try:
                cp(ex_file, newfile)
                click.secho(f"✓ Migrated {newfile}", fg="green")
            except:
                click.secho(f"✗ Failed to migrate {newfile}", fg="red")
                raise
        click.secho(
            "✓ Successfully migrated example Gunicorn configuration",
            fg="green",
            bold=True,
        )
    except:
        click.secho(
            "✗ Error migrating example Gunicorn configuration", fg="red", bold=True
        )
        raise


@hg.command()
@click.option("--dir", default="/etc/systemd/system")
def migratesystemd(dir):
    """Copies example systemd service file to /etc/systemd/system/"""
    try:
        click.secho("Migrating example systemd service...", fg="cyan")
        hyperglass_root = os.path.dirname(hyperglass.__file__)
        ex_file_base = "hyperglass.service.example"
        ex_file = os.path.join(hyperglass_root, ex_file_base)
        basefile, extension = os.path.splitext(ex_file_base)
        newfile = os.path.join(dir, basefile)
        if os.path.exists(newfile):
            click.secho(f"{newfile} already exists", fg="blue")
        else:
            try:
                cp(ex_file, newfile)
                click.secho(f"✓ Migrated {newfile}", fg="green")
            except:
                click.secho(f"✗ Failed to migrate {newfile}", fg="red")
                raise
        click.secho(
            f"✓ Successfully migrated example systemd service to: {newfile}",
            fg="green",
            bold=True,
        )
    except:
        click.secho("✗ Error migrating example systemd service", fg="red", bold=True)
        raise


@hg.command()
@click.option("--user", default="www-data")
@click.option("--group", default="www-data")
def fixpermissions(user, group):
    """Effectively runs `chmod` and `chown` on the hyperglass/hyperglass directory"""
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
