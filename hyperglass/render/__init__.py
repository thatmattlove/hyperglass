# https://github.com/checktheroads/hyperglass
"""
Renders Jinja2 & Sass templates for use by the front end application
"""
# Standard Imports
import os
import logging
import subprocess

# Module Imports
import sass
import toml
import jinja2
import logzero
from logzero import logger
from markdown2 import Markdown
from flask import render_template

# Project Imports
import hyperglass
from hyperglass import configuration

# Module Directories
working_directory = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)
file_loader = jinja2.FileSystemLoader(working_directory)
env = jinja2.Environment(loader=file_loader)

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)

# Configuration Imports
config = configuration.params()
# branding = configuration.branding()
# general = configuration.general()
networks = configuration.networks()

default_details = {
    "footer": """
+++
+++
By using {{ branding["site_name"] }}, you agree to be bound by the following terms of use: All \
queries executed on this page are logged for analysis and troubleshooting. Users are prohibited \
from automating queries, or attempting to process queries in bulk. This service is provided on a \
best effort basis, and {{ general["org_name"] }} makes no availability or performance warranties or \
guarantees whatsoever.
""",
    "bgp_aspath": r"""
+++
title = "Supported AS Path Patterns"
+++
{{ branding["site_name"] }} accepts the following `AS_PATH` regular expression patterns:

| Expression           | Match                                         |
| :------------------- | :-------------------------------------------- |
| `_65000$`            | Originated by 65000                           |
| `^65000_`            | Received from 65000                           |
| `_65000_`            | Via 65000                                     |
| `_65000_65001_`      | Via 65000 and 65001                           |
| `_65000(_.+_)65001$` | Anything from 65001 that passed through 65000 |
""",
    "bgp_community": """
+++
title = "BGP Communities"
+++
{{ branding["site_name"] }} makes use of the following BGP communities:

| Community | Description |
| :-------- | :---------- |
| `65000:1` | Example 1   |
| `65000:2` | Example 2   |
| `65000:3` | Example 3   |
""",
}

default_info = {
    "bgp_route": """
+++
+++
Performs BGP table lookup based on IPv4/IPv6 prefix.
""",
    "bgp_community": """
+++
link = '<a href="#" onclick="bgpHelpCommunity()">{{ general["org_name"] }} BGP Communities</a>'
+++
Performs BGP table lookup based on [Extended](https://tools.ietf.org/html/rfc4360) or \
[Large](https://tools.ietf.org/html/rfc8195) community value.

{{ info["bgp_community"]["link"] }}
""",
    "bgp_aspath": """
+++
link = '<a href="#" onclick="bgpHelpASPath()">Supported BGP AS Path Expressions</a>'
+++
Performs BGP table lookup based on `AS_PATH` regular expression.

{{ info["bgp_aspath"]["link"] }}
""",
    "ping": """
+++
+++
Sends 5 ICMP echo requests to the target.
""",
    "traceroute": """
+++
+++
Performs UDP Based traceroute to the target.<br>For information about how to interpret traceroute \
results, [click here](https://hyperglass.readthedocs.io/nanog_traceroute.pdf).
""",
}


def info(file_name):
    """Converts Markdown documents to HTML, renders Jinja2 variables, renders TOML frontmatter \
    variables, returns dictionary of variables and HTML content"""
    html_classes = {"table": "table"}
    markdown = Markdown(
        extras={
            "break-on-newline": True,
            "code-friendly": True,
            "tables": True,
            "html-classes": html_classes,
        }
    )
    file = os.path.join(working_directory, f"templates/info/{file_name}.md")
    frontmatter_dict = {}
    if os.path.exists(file):
        with open(file, "r") as file_raw:
            file_read = file_raw.read()
            _, frontmatter, content = file_read.split("+++")
            frontmatter_dict[file_name] = toml.loads(frontmatter)
        md_template_fm = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            frontmatter
        )
        md_template_content = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content
        )
    else:
        _, frontmatter, content = default_info[file_name].split("+++")
        md_template_fm = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            frontmatter
        )
        md_template_content = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content
        )
    frontmatter_rendered = md_template_fm.render(**config)
    frontmatter_dict[file_name] = toml.loads(frontmatter_rendered)
    content_rendered = md_template_content.render(**config, info=frontmatter_dict)
    frontmatter_dict[file_name]["content"] = markdown.convert(content_rendered)
    return frontmatter_dict


def details(file_name):
    """Converts Markdown documents to HTML, renders Jinja2 variables, renders TOML frontmatter \
    variables, returns dictionary of variables and HTML content"""
    html_classes = {"table": "table"}
    markdown = Markdown(
        extras={
            "break-on-newline": True,
            "code-friendly": True,
            "tables": True,
            "html-classes": html_classes,
        }
    )
    file = os.path.join(working_directory, f"templates/info/details/{file_name}.md")
    frontmatter_dict = {}
    if os.path.exists(file):
        with open(file, "r") as file_raw:
            file_read = file_raw.read()
            _, frontmatter, content = file_read.split("+++")
        md_template_fm = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            frontmatter
        )
        md_template_content = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content
        )
    else:
        _, frontmatter, content = default_details[file_name].split("+++")
        frontmatter_dict[file_name] = toml.loads(frontmatter)
        md_template_fm = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            frontmatter
        )
        md_template_content = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content
        )
    frontmatter_rendered = md_template_fm.render(**config)
    frontmatter_dict[file_name] = toml.loads(frontmatter_rendered)
    content_rendered = md_template_content.render(**config, details=frontmatter_dict)
    frontmatter_dict[file_name]["content"] = markdown.convert(content_rendered)
    return frontmatter_dict


def html(template_name):
    """Renders Jinja2 HTML templates"""
    details_name_list = ["footer", "bgp_aspath", "bgp_community"]
    details_dict = {}
    for details_name in details_name_list:
        details_data = details(details_name)
        details_dict.update(details_data)
    info_list = ["bgp_route", "bgp_aspath", "bgp_community", "ping", "traceroute"]
    info_dict = {}
    for info_name in info_list:
        info_data = info(info_name)
        info_dict.update(info_data)
    template = env.get_template(f"templates/{template_name}.html")
    return template.render(
        **config, info=info_dict, details=details_dict, networks=networks
    )


def css():
    """Renders Jinja2 template to Sass file, then compiles Sass as CSS"""
    scss_file = os.path.join(hyperglass_root, "static/sass/hyperglass.scss")
    css_file = os.path.join(hyperglass_root, "static/css/hyperglass.css")
    # Renders Jinja2 template as Sass file
    try:
        template_file = "templates/hyperglass.scss"
        template = env.get_template(template_file)
        rendered_output = template.render(**config)
        with open(scss_file, "w") as scss_output:
            scss_output.write(rendered_output)
    except:
        logger.error(f"Error rendering Jinja2 template {template_file}.")
        raise
    # Compiles Sass to CSS
    try:
        generated_sass = sass.compile(filename=scss_file)
        with open(css_file, "w") as css_output:
            css_output.write(generated_sass)
            logger.debug(f"Compiled Sass file {scss_file} to CSS file {css_file}.")
    except:
        logger.error(f"Error compiling Sass in file {scss_file}.")
        raise
