from flask import render_template
import vars
import jinja2
import subprocess
import codecs
from markdown2 import Markdown
import sass

file_loader = jinja2.FileSystemLoader(".")
env = jinja2.Environment(loader=file_loader)

# Converts templates/footer.md from Markdown to HTML
md = Markdown()
footer_file = env.get_template("templates/footer.md")
footer_jinja = footer_file.render(title=vars.brand.title())
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
            primary_asn=vars.gen.primary_asn(),
            google_analytics=vars.gen.google_analytics(),
            enable_recaptcha=vars.gen.enable_recaptcha(),
            enable_bgp_route=vars.gen.enable_bgp_route(),
            enable_bgp_community=vars.gen.enable_bgp_community(),
            enable_bgp_aspath=vars.gen.enable_bgp_aspath(),
            enable_ping=vars.gen.enable_ping(),
            enable_traceroute=vars.gen.enable_traceroute(),
            cache_timeout=vars.gen.cache_timeout(),
            message_rate_limit_query=vars.gen.message_rate_limit_query(),
            # Branding
            site_title=vars.brand.site_title(),
            title=vars.brand.title(),
            subtitle=vars.brand.subtitle(),
            title_mode=vars.brand.title_mode(),
            color_hero=vars.brand.color_hero(),
            enable_credit=vars.brand.enable_credit(),
            enable_footer=vars.brand.enable_footer(),
            footer_content=md.convert(footer),
            logo_path=vars.brand.logo_path(),
            logo_width=vars.brand.logo_width(),
            placeholder_prefix=vars.brand.placeholder_prefix(),
            show_peeringdb=vars.brand.show_peeringdb(),
            text_results=vars.brand.text_results(),
            text_location=vars.brand.text_location(),
            text_cache=vars.brand.text_cache(),
            text_415_title=vars.brand.text_415_title(),
            text_415_subtitle=vars.brand.text_415_subtitle(),
            text_415_button=vars.brand.text_415_button(),
            text_help_bgp_route=vars.brand.text_help_bgp_route(),
            text_help_bgp_community=vars.brand.text_help_bgp_community(),
            text_help_bgp_aspath=vars.brand.text_help_bgp_aspath(),
            text_help_ping=vars.brand.text_help_ping(),
            text_help_traceroute=vars.brand.text_help_traceroute(),
            text_limiter_title=vars.brand.text_limiter_title(),
            text_limiter_subtitle=vars.brand.text_limiter_subtitle(),
            # Devices
            device_networks=vars.dev.networks(),
            # device_location=vars.dev.location(),
            device_name=vars.dev.name(),
        )


class css:
    def renderTemplate():
        try:
            template = env.get_template("templates/hyperglass.scss")
            rendered_output = template.render(
                color_btn_submit=vars.brand.color_btn_submit(),
                color_progressbar=vars.brand.color_progressbar(),
                color_tag_loctitle=vars.brand.color_tag_loctitle(),
                color_tag_cmdtitle=vars.brand.color_tag_cmdtitle(),
                color_tag_cmd=vars.brand.color_tag_cmd(),
                color_tag_loc=vars.brand.color_tag_loc(),
                color_hero=vars.brand.color_hero(),
                primary_font_url=vars.brand.primary_font_url(),
                primary_font_name=vars.brand.primary_font_name(),
                mono_font_url=vars.brand.mono_font_url(),
                mono_font_name=vars.brand.mono_font_name(),
            )
            with open("static/sass/hyperglass.scss", "w") as scss_output:
                scss_output.write(rendered_output)
        except:
            raise TypeError("Error rendering Jinja2 template.")
        try:
            generated_sass = sass.compile(filename="static/sass/hyperglass.scss")
            with open("static/css/hyperglass.css", "w") as css_output:
                css_output.write(generated_sass)
                print("\n", "* Sass templates rendered to CSS files.", "\n")
        except:
            raise TypeError("Error rendering Sass template.")
