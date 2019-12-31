"""Renders Jinja2 & Sass templates for use by the front end application."""

# Standard Library Imports
import asyncio
import json
import time
from pathlib import Path

# Third Party Imports
import aiofiles
import jinja2

# Project Imports
from hyperglass.configuration import frontend_devices
from hyperglass.configuration import frontend_networks
from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.util import log

# Module Directories
working_directory = Path(__file__).resolve().parent
hyperglass_root = working_directory.parent
file_loader = jinja2.FileSystemLoader(str(working_directory))
env = jinja2.Environment(
    loader=file_loader,
    autoescape=True,
    extensions=["jinja2.ext.autoescape"],
    enable_async=True,
)


async def render_frontend_config():
    """Render user config to JSON for use by frontend."""
    rendered_frontend_file = hyperglass_root.joinpath("static/src/js/frontend.json")
    try:
        async with aiofiles.open(rendered_frontend_file, mode="w") as frontend_file:
            await frontend_file.write(
                json.dumps(
                    {
                        "config": frontend_params,
                        "networks": frontend_networks,
                        "devices": frontend_devices,
                    }
                )
            )
    except Exception as frontend_error:
        raise HyperglassError(f"Error rendering front end config: {frontend_error}")


async def get_fonts():
    """Download Google fonts."""
    font_dir = hyperglass_root.joinpath("static/src/sass/fonts")
    font_bin = str(
        hyperglass_root.joinpath("static/src/node_modules/get-google-fonts/cli.js")
    )
    font_base = "https://fonts.googleapis.com/css?family={p}|{m}&display=swap"
    font_primary = "+".join(params.branding.font.primary.split(" ")).strip()
    font_mono = "+".join(params.branding.font.mono.split(" ")).strip()
    font_url = font_base.format(p=font_primary + ":300,400,700", m=font_mono + ":400")
    command = f"node {str(font_bin)} -w -i '{font_url}' -o {str(font_dir)}"
    try:
        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        for line in stdout.decode().strip().split("\n"):
            log.debug(line)
        if proc.returncode != 0:
            output_error = stderr.decode("utf-8")
            log.error(output_error)
            raise RuntimeError(f"Error downloading font from URL {font_url}")
        await proc.wait()
    except Exception as e:
        raise HyperglassError(str(e))


async def render_theme():
    """Render Jinja2 template to Sass file."""
    rendered_theme_file = hyperglass_root.joinpath("static/src/sass/theme.sass")
    try:
        template = env.get_template("templates/theme.sass.j2")
        rendered_theme = await template.render_async(params.branding)

        log.debug(f"Branding variables:\n{params.branding.json(indent=4)}")
        log.debug(f"Rendered theme:\n{str(rendered_theme)}")
        async with aiofiles.open(rendered_theme_file, mode="w") as theme_file:
            await theme_file.write(rendered_theme)
    except jinja2.exceptions as theme_error:
        raise HyperglassError(f"Error rendering theme: {theme_error}")


async def build_assets():
    """Build, bundle, and minify Sass/CSS/JS web assets."""
    command = "yarn --silent --emoji false --json --no-progress build"
    static_dir = hyperglass_root.joinpath("static/src")
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=static_dir,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        output_out = json.loads(stdout.decode("utf-8").split("\n")[0])
        if proc.returncode != 0:
            output_error = json.loads(stderr.decode("utf-8").strip("\n"))
            raise RuntimeError(
                f'Error building web assets with script {output_out["data"]}:'
                f'{output_error["data"]}'
            )
        await proc.wait()
    except Exception as e:
        raise HyperglassError(str(e))
    log.debug(f'Built web assets with script {output_out["data"]}')


def render_assets():
    """Run web asset rendering functions."""
    start = time.time()
    try:
        log.debug("Rendering front end config...")
        asyncio.run(render_frontend_config())
        log.debug("Rendered front end config")
    except HyperglassError as frontend_error:
        raise HyperglassError(str(frontend_error))

    try:
        log.debug("Downloading theme fonts...")
        asyncio.run(get_fonts())
        log.debug("Downloaded theme fonts")
    except HyperglassError as theme_error:
        raise HyperglassError(str(theme_error))

    try:
        log.debug("Rendering theme elements...")
        asyncio.run(render_theme())
        log.debug("Rendered theme elements")
    except HyperglassError as theme_error:
        raise HyperglassError(str(theme_error))

    try:
        log.debug("Building web assets...")
        asyncio.run(build_assets())
        log.debug("Built web assets")
    except HyperglassError as assets_error:
        raise HyperglassError(str(assets_error))
    end = time.time()
    elapsed = round(end - start, 2)
    log.debug(f"Rendered assets in {elapsed} seconds.")
