#!/usr/bin/env python3
import os
import sass
import jinja2
import subprocess
from logzero import logger
from markdown2 import Markdown
from flask import render_template

import hyperglass
from hyperglass import configuration

dir = os.path.dirname(os.path.abspath(__file__))
hyperglass_root = os.path.dirname(hyperglass.__file__)
file_loader = jinja2.FileSystemLoader(dir)
env = jinja2.Environment(loader=file_loader)

branding = configuration.branding()
general = configuration.general()
networks = configuration.networks()


# Functions for rendering Jinja2 templates & importing variables


class html:
    def renderTemplate(t):

        # Converts templates/footer.md from Markdown to HTML
        md = Markdown()
        footer_template = env.get_template("templates/footer.md")
        footer_jinja = footer_template.render(
            site_title=branding.site_title, org_name=general.org_name
        )
        if t == "index":
            template = env.get_template("templates/index.html")
        elif t == "429":
            template = env.get_template("templates/429.html")
        elif t == "500":
            template = env.get_template("templates/500.html")
        return template.render(
            # General
            primary_asn=general.primary_asn,
            org_name=general.org_name,
            google_analytics=general.google_analytics,
            enable_bgp_route=general.enable_bgp_route,
            enable_bgp_community=general.enable_bgp_community,
            enable_bgp_aspath=general.enable_bgp_aspath,
            enable_ping=general.enable_ping,
            enable_traceroute=general.enable_traceroute,
            cache_timeout=general.cache_timeout,
            message_rate_limit_query=general.message_rate_limit_query,
            # Branding
            site_title=branding.site_title,
            title=branding.title,
            subtitle=branding.subtitle,
            title_mode=branding.title_mode,
            color_bg=branding.color_bg,
            color_danger=branding.color_danger,
            color_btn_submit=branding.color_btn_submit,
            color_progressbar=branding.color_progressbar,
            color_tag_loctitle=branding.color_tag_loctitle,
            color_tag_cmdtitle=branding.color_tag_cmdtitle,
            color_tag_cmd=branding.color_tag_cmd,
            color_tag_loc=branding.color_tag_loc,
            enable_credit=branding.enable_credit,
            enable_footer=branding.enable_footer,
            footer_content=md.convert(footer_jinja),
            logo_path=branding.logo_path,
            logo_width=branding.logo_width,
            favicon16_path=branding.favicon16_path,
            favicon32_path=branding.favicon32_path,
            placeholder_prefix=branding.placeholder_prefix,
            show_peeringdb=branding.show_peeringdb,
            text_results=branding.text_results,
            text_location=branding.text_location,
            text_cache=branding.text_cache,
            text_500_title=branding.text_500_title,
            text_500_subtitle=branding.text_500_subtitle,
            text_500_button=branding.text_500_button,
            text_help_bgp_route=branding.text_help_bgp_route,
            text_help_bgp_community=branding.text_help_bgp_community,
            text_help_bgp_aspath=branding.text_help_bgp_aspath,
            text_help_ping=branding.text_help_ping,
            text_help_traceroute=branding.text_help_traceroute,
            text_limiter_title=branding.text_limiter_title,
            text_limiter_subtitle=branding.text_limiter_subtitle,
            # Devices
            device_networks=configuration.networks(),
        )


class css:
    def renderTemplate():
        scss_file = os.path.join(hyperglass_root, "static/sass/hyperglass.scss")
        css_file = os.path.join(hyperglass_root, "static/css/hyperglass.css")
        try:
            template = env.get_template("templates/hyperglass.scss")
            rendered_output = template.render(
                color_btn_submit=branding.color_btn_submit,
                color_progressbar=branding.color_progressbar,
                color_tag_loctitle=branding.color_tag_loctitle,
                color_tag_cmdtitle=branding.color_tag_cmdtitle,
                color_tag_cmd=branding.color_tag_cmd,
                color_tag_loc=branding.color_tag_loc,
                color_bg=branding.color_bg,
                color_danger=branding.color_danger,
                primary_font_url=branding.primary_font_url,
                primary_font_name=branding.primary_font_name,
                mono_font_url=branding.mono_font_url,
                mono_font_name=branding.mono_font_name,
            )
            with open(scss_file, "w") as scss_output:
                scss_output.write(rendered_output)
        except:
            logger.error("Error rendering Jinja2 template.")
            raise TypeError("Error rendering Jinja2 template.")
        try:
            generated_sass = sass.compile(filename=scss_file)
            with open(css_file, "w") as css_output:
                css_output.write(generated_sass)
                logger.info("Rendered Sass templates to CSS files.")
        except:
            logger.error("Error rendering Sass template.")
            raise
