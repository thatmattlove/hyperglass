#!/usr/bin/env python3
import os
import sass
import codecs
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

# Converts templates/footer.md from Markdown to HTML
md = Markdown()
footer_template = env.get_template("templates/footer.md")
footer_jinja = footer_template.render(title=configuration.brand.title())
footer = footer_jinja

# Functions for rendering Jinja2 templates & importing variables


class html:
    def renderTemplate(t):
        if t == "index":
            template = env.get_template("templates/index.html")
        elif t == "429":
            template = env.get_template("templates/429.html")
        elif t == "415":
            template = env.get_template("templates/415.html")
        elif t == "test":
            template = env.get_template("templates/429.html")
        return template.render(
            # General
            primary_asn=configuration.gen.primary_asn(),
            google_analytics=configuration.gen.google_analytics(),
            enable_recaptcha=configuration.gen.enable_recaptcha(),
            enable_bgp_route=configuration.gen.enable_bgp_route(),
            enable_bgp_community=configuration.gen.enable_bgp_community(),
            enable_bgp_aspath=configuration.gen.enable_bgp_aspath(),
            enable_ping=configuration.gen.enable_ping(),
            enable_traceroute=configuration.gen.enable_traceroute(),
            cache_timeout=configuration.gen.cache_timeout(),
            message_rate_limit_query=configuration.gen.message_rate_limit_query(),
            # Branding
            site_title=configuration.brand.site_title(),
            title=configuration.brand.title(),
            subtitle=configuration.brand.subtitle(),
            title_mode=configuration.brand.title_mode(),
            color_bg=configuration.brand.color_bg(),
            color_btn_submit=configuration.brand.color_btn_submit(),
            color_progressbar=configuration.brand.color_progressbar(),
            color_tag_loctitle=configuration.brand.color_tag_loctitle(),
            color_tag_cmdtitle=configuration.brand.color_tag_cmdtitle(),
            color_tag_cmd=configuration.brand.color_tag_cmd(),
            color_tag_loc=configuration.brand.color_tag_loc(),
            enable_credit=configuration.brand.enable_credit(),
            enable_footer=configuration.brand.enable_footer(),
            footer_content=md.convert(footer),
            logo_path=configuration.brand.logo_path(),
            logo_width=configuration.brand.logo_width(),
            placeholder_prefix=configuration.brand.placeholder_prefix(),
            show_peeringdb=configuration.brand.show_peeringdb(),
            text_results=configuration.brand.text_results(),
            text_location=configuration.brand.text_location(),
            text_cache=configuration.brand.text_cache(),
            text_415_title=configuration.brand.text_415_title(),
            text_415_subtitle=configuration.brand.text_415_subtitle(),
            text_415_button=configuration.brand.text_415_button(),
            text_help_bgp_route=configuration.brand.text_help_bgp_route(),
            text_help_bgp_community=configuration.brand.text_help_bgp_community(),
            text_help_bgp_aspath=configuration.brand.text_help_bgp_aspath(),
            text_help_ping=configuration.brand.text_help_ping(),
            text_help_traceroute=configuration.brand.text_help_traceroute(),
            text_limiter_title=configuration.brand.text_limiter_title(),
            text_limiter_subtitle=configuration.brand.text_limiter_subtitle(),
            # Devices
            device_networks=configuration.dev.networks(),
            # device_location=configuration.dev.location(),
            device_name=configuration.dev.name(),
        )


class css:
    def renderTemplate():
        scss_file = os.path.join(hyperglass_root, "static/sass/hyperglass.scss")
        css_file = os.path.join(hyperglass_root, "static/css/hyperglass.css")
        try:
            template = env.get_template("templates/hyperglass.scss")
            rendered_output = template.render(
                color_btn_submit=configuration.brand.color_btn_submit(),
                color_progressbar=configuration.brand.color_progressbar(),
                color_tag_loctitle=configuration.brand.color_tag_loctitle(),
                color_tag_cmdtitle=configuration.brand.color_tag_cmdtitle(),
                color_tag_cmd=configuration.brand.color_tag_cmd(),
                color_tag_loc=configuration.brand.color_tag_loc(),
                color_bg=configuration.brand.color_bg(),
                primary_font_url=configuration.brand.primary_font_url(),
                primary_font_name=configuration.brand.primary_font_name(),
                mono_font_url=configuration.brand.mono_font_url(),
                mono_font_name=configuration.brand.mono_font_name(),
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
