# https://github.com/checktheroads/hyperglass
"""
Renders Jinja2 & Sass templates for use by the front end application
"""
# Standard Imports
import os
import subprocess

# Module Imports
import sass
import toml
import jinja2
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

# Configuration Imports
branding = configuration.branding()
general = configuration.general()
networks = configuration.networks()

defaults = {
    "footer": """
+++
+++
By using {{ site_title }}, you agree to be bound by the following terms of use: All queries \
executed on this page are logged for analysis and troubleshooting. Users are prohibited from \
automating queries, or attempting to process queries in bulk. This service is provided on a best \
effort basis, and {{ org_name }} makes no availability or performance warranties or guarantees \
whatsoever.
""",
    "bgp_aspath": r"""
+++
title = "Supported AS Path Patterns"
+++
{{ site_title }} accepts the following `AS_PATH` regular expression patterns:

| Expression               |                                                 Match |
| :----------------------- | ----------------------------------------------------: |
| `_65000$`                |                                 Originated by AS65000 |
| `^65000\_`               |                                 Received from AS65000 |
| `_65000_`                |                                           Via AS65000 |
| `_65000_65001_`          |                               Via AS65000 and AS65001 |
| `_65000(_.+_)65001$`     |     Anything from AS65001 that passed through AS65000 |
""",
    "bgp_community": """
+++
title = "BGP Communities"
+++
{{ site_title }} makes use of the following BGP communities:

| Community | Description |
| :-------- | :---------- |
| `65000:1` | Example 1   |
| `65000:2` | Example 2   |
| `65000:3` | Example 3   |
""",
}


def content(file_name):
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
    delim = "+++"
    file = os.path.join(working_directory, f"templates/content/{file_name}.md")
    frontmatter_dict = None
    if os.path.exists(file):
        with open(file, "r") as file_raw:
            file_read = file_raw.read()
            _, frontmatter, content_md = file_read.split(delim)
            frontmatter_dict = {file_name: toml.loads(frontmatter)}
        content_md_template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content_md
        )
    else:
        content_read = defaults[file_name]
        _, frontmatter, content_md = content_read.split(delim)
        frontmatter_dict = {file_name: toml.loads(frontmatter)}
        content_md_template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            content_md
        )
    content_rendered = content_md_template.render(
        **general, **branding, **frontmatter_dict
    )
    content_html = markdown.convert(content_rendered)
    frontmatter_dict[file_name]["content"] = content_html
    return frontmatter_dict


def html(t):
    """Renders Jinja2 HTML templates"""
    content_name_list = ["footer", "bgp_aspath", "bgp_community"]
    content_dict = {}
    for content_name in content_name_list:
        # content_file = os.path.join(working_directory, f"templates/content/{c}.md")
        content_data = content(content_name)
        content_dict.update(content_data)
    if t == "index":
        template = env.get_template("templates/index.html")
    elif t == "429":
        template = env.get_template("templates/429.html")
    elif t == "500":
        template = env.get_template("templates/500.html")
    return template.render(
        **general, **branding, **content_dict, device_networks=networks
    )


def css():
    """Renders Jinja2 template to Sass file, then compiles Sass as CSS"""
    scss_file = os.path.join(hyperglass_root, "static/sass/hyperglass.scss")
    css_file = os.path.join(hyperglass_root, "static/css/hyperglass.css")
    # Renders Jinja2 template as Sass file
    try:
        template_file = "templates/hyperglass.scss"
        template = env.get_template(template_file)
        rendered_output = template.render(**branding)
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
            logger.info(f"Compiled Sass file {scss_file} to CSS file {css_file}.")
    except:
        logger.error(f"Error compiling Sass in file {scss_file}.")
        raise
