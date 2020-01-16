"""Renders Jinja2 & Sass templates for use by the front end application."""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
import jinja2
import yaml
from aiofile import AIOFile
from markdown2 import Markdown

# Project Imports
from hyperglass.configuration import devices
from hyperglass.configuration import networks
from hyperglass.configuration import params
from hyperglass.constants import DEFAULT_DETAILS
from hyperglass.constants import DEFAULT_HELP
from hyperglass.constants import DEFAULT_TERMS
from hyperglass.exceptions import ConfigError
from hyperglass.exceptions import HyperglassError
from hyperglass.util import log

# Module Directories
WORKING_DIR = Path(__file__).resolve().parent
JINJA_LOADER = jinja2.FileSystemLoader(str(WORKING_DIR))
JINJA_ENV = jinja2.Environment(
    loader=JINJA_LOADER,
    autoescape=True,
    extensions=["jinja2.ext.autoescape"],
    enable_async=True,
)

_MD_CONFIG = {
    "extras": {
        "break-on-newline": True,
        "code-friendly": True,
        "tables": True,
        "html-classes": {"table": "table"},
    }
}
MARKDOWN = Markdown(**_MD_CONFIG)


async def parse_md(raw_file):
    file_list = raw_file.split("---", 2)
    file_list_len = len(file_list)
    if file_list_len == 1:
        fm = {}
        content = file_list[0]
    elif file_list_len == 3 and file_list[1].strip():
        try:
            fm = yaml.safe_load(file_list[1])
        except yaml.YAMLError as ye:
            raise ConfigError(str(ye)) from None
        content = file_list[2]
    else:
        fm = {}
        content = ""
    return (fm, content)


async def get_file(path_obj):
    async with AIOFile(path_obj, "r") as raw_file:
        file = await raw_file.read()
        return file


async def render_help():
    if params.branding.help_menu.file is not None:
        help_file = await get_file(params.branding.help_menu.file)
    else:
        help_file = DEFAULT_HELP

    fm, content = await parse_md(help_file)

    content_template = JINJA_ENV.from_string(content)
    content_rendered = await content_template.render_async(params, info=fm)

    return {"content": MARKDOWN.convert(content_rendered), **fm}


async def render_terms():

    if params.branding.terms.file is not None:
        terms_file = await get_file(params.branding.terms.file)
    else:
        terms_file = DEFAULT_TERMS

    fm, content = await parse_md(terms_file)
    content_template = JINJA_ENV.from_string(content)
    content_rendered = await content_template.render_async(params, info=fm)

    return {"content": MARKDOWN.convert(content_rendered), **fm}


async def render_details():
    details = []
    for vrf in devices.vrf_objects:
        detail = {"name": vrf.name, "display_name": vrf.display_name}
        info_attrs = ("bgp_aspath", "bgp_community")
        command_info = []
        for attr in info_attrs:
            file = getattr(vrf.info, attr)
            if file is not None:
                raw_content = await get_file(file)
                fm, content = await parse_md(raw_content)
            else:
                fm, content = await parse_md(DEFAULT_DETAILS[attr])

            content_template = JINJA_ENV.from_string(content)
            content_rendered = await content_template.render_async(params, info=fm)
            content_html = MARKDOWN.convert(content_rendered)

            command_info.append(
                {
                    "id": f"{vrf.name}-{attr}",
                    "name": attr,
                    "frontmatter": fm,
                    "content": content_html,
                }
            )

        detail.update({"commands": command_info})
        details.append(detail)
    return details


async def render_html(template_name, **kwargs):
    """Render Jinja2 HTML templates.

    Arguments:
        template_name {str} -- Jinja2 template name

    Raises:
        HyperglassError: Raised if template is not found

    Returns:
        {str} -- Rendered template
    """
    try:
        template_file = f"templates/{template_name}.html.j2"
        template = JINJA_ENV.get_template(template_file)

    except jinja2.TemplateNotFound as template_error:
        log.error(
            f"Error rendering Jinja2 template {str(Path(template_file).resolve())}."
        )
        raise HyperglassError(template_error)

    rendered_help = await render_help()
    rendered_terms = await render_terms()
    rendered_details = await render_details()

    sub_templates = {
        "details": rendered_details,
        "help": rendered_help,
        "terms": rendered_terms,
        "networks": networks,
        **kwargs,
    }

    return await template.render_async(params, **sub_templates)


# async def generate_markdown(section, file_name=None):
#     """Render markdown as HTML.

#     Arguments:
#         section {str} -- Section name

#     Keyword Arguments:
#         file_name {str} -- Markdown file name (default: {None})

#     Raises:
#         HyperglassError: Raised if YAML front matter is unreadable

#     Returns:
#         {dict} -- Frontmatter dictionary
#     """
#     if section == "help" and params.branding.help_menu.file is not None:
#         info = await get_file(params.branding.help_menu.file)
#     elif section == "help" and params.branding.help_menu.file is None:
#         info = DEFAULT_HELP
#     elif section == "details":
#         file = WORKING_DIR.joinpath(f"templates/info/details/{file_name}.md")
#         if file.exists():
#             with file.open(mode="r") as file_raw:
#                 yaml_raw = file_raw.read()
#         else:
#             yaml_raw = DEFAULT_DETAILS[file_name]
#     _, frontmatter, content = yaml_raw.split("---", 2)
#     md_config = {
#         "extras": {
#             "break-on-newline": True,
#             "code-friendly": True,
#             "tables": True,
#             "html-classes": {"table": "table"},
#         }
#     }
#     markdown = Markdown(**md_config)

#     frontmatter_rendered = JINJA_ENV.from_string(frontmatter).render(params)

#     if frontmatter_rendered:
#         frontmatter_loaded = yaml.safe_load(frontmatter_rendered)
#     elif not frontmatter_rendered:
#         frontmatter_loaded = {"frontmatter": None}

#     content_rendered = await JINJA_ENV.from_string(content).render_async(
#         params, info=frontmatter_loaded
#     )

#     help_dict = dict(content=markdown.convert(content_rendered), **frontmatter_loaded)
#     if not help_dict:
#         raise HyperglassError(f"Error reading YAML frontmatter for {file_name}")
#     return help_dict


# async def render_html(template_name, **kwargs):
#     """Render Jinja2 HTML templates.

#     Arguments:
#         template_name {str} -- Jinja2 template name

#     Raises:
#         HyperglassError: Raised if template is not found

#     Returns:
#         {str} -- Rendered template
#     """
#     detail_items = ("footer", "bgp_aspath", "bgp_community")
#     details = {}

#     for details_name in detail_items:
#         details_data = await generate_markdown("details", details_name)
#         details.update({details_name: details_data})

#     rendered_help = await generate_markdown("help")

#     try:
#         template_file = f"templates/{template_name}.html.j2"
#         template = JINJA_ENV.get_template(template_file)

#     except jinja2.TemplateNotFound as template_error:
#         log.error(f"Error rendering Jinja2 template {Path(template_file).resolve()}.")
#         raise HyperglassError(template_error)

#     return await template.render_async(
#         params,
#         rendered_help=rendered_help,
#         details=details,
#         networks=networks,
#         **kwargs,
#     )
