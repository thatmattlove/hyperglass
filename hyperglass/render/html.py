"""
Renders Jinja2 & Sass templates for use by the front end application
"""
# Standard Library Imports
from pathlib import Path

# Third Party Imports
import jinja2
import yaml
from logzero import logger as log
from markdown2 import Markdown

# Project Imports
from hyperglass.configuration import devices
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.configuration import params, networks
from hyperglass.exceptions import HyperglassError

# Module Directories
working_directory = Path(__file__).resolve().parent
hyperglass_root = working_directory.parent
file_loader = jinja2.FileSystemLoader(str(working_directory))
env = jinja2.Environment(
    loader=file_loader, autoescape=True, extensions=["jinja2.ext.autoescape"]
)

default_details = {
    "footer": """
---
template: footer
---
By using {{ branding.site_name }}, you agree to be bound by the following terms of \
use: All queries executed on this page are logged for analysis and troubleshooting. \
Users are prohibited from automating queries, or attempting to process queries in \
bulk. This service is provided on a best effort basis, and {{ general.org_name }} \
makes no availability or performance warranties or guarantees whatsoever.
""",
    "bgp_aspath": r"""
---
template: bgp_aspath
title: Supported AS Path Patterns
---
{{ branding.site_name }} accepts the following `AS_PATH` regular expression patterns:

| Expression           | Match                                         |
| :------------------- | :-------------------------------------------- |
| `_65000$`            | Originated by 65000                           |
| `^65000_`            | Received from 65000                           |
| `_65000_`            | Via 65000                                     |
| `_65000_65001_`      | Via 65000 and 65001                           |
| `_65000(_.+_)65001$` | Anything from 65001 that passed through 65000 |
""",
    "bgp_community": """
---
template: bgp_community
title: BGP Communities
---
{{ branding.site_name }} makes use of the following BGP communities:

| Community | Description |
| :-------- | :---------- |
| `65000:1` | Example 1   |
| `65000:2` | Example 2   |
| `65000:3` | Example 3   |
""",
}

default_info = {
    "bgp_route": """
---
template: bgp_route
---
Performs BGP table lookup based on IPv4/IPv6 prefix.
""",
    "bgp_community": """
---
template: bgp_community
---
Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360" target\
="_blank">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195" target=\
"_blank">Large</a> community value.

""",
    "bgp_aspath": """
---
template: bgp_aspath
---
Performs BGP table lookup based on `AS_PATH` regular expression.

""",
    "ping": """
---
template: ping
---
Sends 5 ICMP echo requests to the target.
""",
    "traceroute": """
---
template: traceroute
---
Performs UDP Based traceroute to the target.<br>For information about how to \
interpret traceroute results, <a href="https://hyperglass.readthedocs.io/en/latest/ass\
ets/traceroute_nanog.pdf" target="_blank">click here</a>.
""",
}


default_help = """
---
template: default_help
---
##### BGP Route
Performs BGP table lookup based on IPv4/IPv6 prefix.
<hr>
##### BGP Community
Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360" target\
="_blank">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195" target=\
"_blank">Large</a> community value.
<hr>
##### BGP AS Path
Performs BGP table lookup based on `AS_PATH` regular expression.
<hr>
##### Ping
Sends 5 ICMP echo requests to the target.
<hr>
##### Traceroute
Performs UDP Based traceroute to the target.<br>For information about how to \
interpret traceroute results, <a href="https://hyperglass.readthedocs.io/en/latest/ass\
ets/traceroute_nanog.pdf" target="_blank">click here</a>.
"""


def generate_markdown(section, file_name=None):
    """
    Renders markdown as HTML. If file_name exists in appropriate
    directory, it will be imported and used. If not, the default values
    will be used. Also renders the Front Matter values within each
    template.
    """
    if section == "help":
        file = working_directory.joinpath("templates/info/help.md")
        if file.exists():
            with file.open(mode="r") as file_raw:
                yaml_raw = file_raw.read()
        else:
            yaml_raw = default_help
    elif section == "details":
        file = working_directory.joinpath(f"templates/info/details/{file_name}.md")
        if file.exists():
            with file.open(mode="r") as file_raw:
                yaml_raw = file_raw.read()
        else:
            yaml_raw = default_details[file_name]
    _, frontmatter, content = yaml_raw.split("---", 2)
    html_classes = {"table": "table"}
    markdown = Markdown(
        extras={
            "break-on-newline": True,
            "code-friendly": True,
            "tables": True,
            "html-classes": html_classes,
        }
    )
    frontmatter_rendered = (
        jinja2.Environment(
            loader=jinja2.BaseLoader,
            autoescape=True,
            extensions=["jinja2.ext.autoescape"],
        )
        .from_string(frontmatter)
        .render(params)
    )
    if frontmatter_rendered:
        frontmatter_loaded = yaml.safe_load(frontmatter_rendered)
    elif not frontmatter_rendered:
        frontmatter_loaded = {"frontmatter": None}
    content_rendered = (
        jinja2.Environment(
            loader=jinja2.BaseLoader,
            autoescape=True,
            extensions=["jinja2.ext.autoescape"],
        )
        .from_string(content)
        .render(params, info=frontmatter_loaded)
    )
    help_dict = dict(content=markdown.convert(content_rendered), **frontmatter_loaded)
    if not help_dict:
        raise HyperglassError(f"Error reading YAML frontmatter for {file_name}")
    return help_dict


def render_html(template_name, **kwargs):
    """Renders Jinja2 HTML templates"""
    details_name_list = ["footer", "bgp_aspath", "bgp_community"]
    details_dict = {}
    for details_name in details_name_list:
        details_data = generate_markdown("details", details_name)
        details_dict.update({details_name: details_data})
    info_list = ["bgp_route", "bgp_aspath", "bgp_community", "ping", "traceroute"]
    rendered_help = generate_markdown("help")
    log.debug(rendered_help)
    try:
        template_file = f"templates/{template_name}.html.j2"
        template = env.get_template(template_file)
        return template.render(
            params,
            rendered_help=rendered_help,
            details=details_dict,
            networks=networks,
            **kwargs,
        )
    except jinja2.TemplateNotFound as template_error:
        log.error(f"Error rendering Jinja2 template {Path(template_file).resolve()}.")
        raise HyperglassError(template_error)
