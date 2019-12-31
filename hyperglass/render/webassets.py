"""Renders Jinja2 & Sass templates for use by the front end application."""

# Standard Library Imports
import asyncio
import json
import time
from pathlib import Path

# Third Party Imports
import jinja2
from aiofile import AIOFile

# Project Imports
from hyperglass.configuration import frontend_devices
from hyperglass.configuration import frontend_networks
from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.util import log

# File & Path Definitions
CWD = Path(__file__).parent
ROOT_DIR = CWD.parent
FRONTEND_CONFIG = ROOT_DIR / "static/src/js/frontend.json"
FONT_DIR = ROOT_DIR / "static/src/sass/fonts"
FONT_CMD = ROOT_DIR / "static/src/node_modules/get-google-fonts/cli.js"
THEME_FILE = ROOT_DIR / "static/src/sass/theme.sass"
STATIC_DIR = ROOT_DIR / "static/src"

# Jinja2 Config
JINJA_FILE_LOADER = jinja2.FileSystemLoader(str(CWD))
JINJA_ENV = jinja2.Environment(
    loader=JINJA_FILE_LOADER,
    autoescape=True,
    extensions=["jinja2.ext.autoescape"],
    enable_async=True,
)


async def _render_frontend_config():
    """Render user config to JSON for use by frontend."""
    log.debug("Rendering front end config...")

    try:
        async with AIOFile(FRONTEND_CONFIG, "w+") as file:
            await file.write(
                json.dumps(
                    {
                        "config": frontend_params,
                        "networks": frontend_networks,
                        "devices": frontend_devices,
                    }
                )
            )
            await file.fsync()
        log.debug("Rendered front end config")
    except Exception as e:
        raise HyperglassError(f"Error rendering front end config: {str(e)}")


async def _get_fonts():
    """Download Google fonts."""
    log.debug("Downloading theme fonts...")

    font_base = "https://fonts.googleapis.com/css?family={p}|{m}&display=swap"
    font_primary = "+".join(params.branding.font.primary.name.split(" ")).strip()
    font_mono = "+".join(params.branding.font.mono.name.split(" ")).strip()
    font_url = font_base.format(p=font_primary + ":300,400,700", m=font_mono + ":400")

    font_command = f"node {str(FONT_CMD)} -w -i '{font_url}' -o {str(FONT_DIR)}"

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=font_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=STATIC_DIR,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        for line in stdout.decode().strip().split("\n"):
            log.debug(line)

        if proc.returncode != 0:
            output_error = stderr.decode("utf-8")
            log.error(output_error)
            raise RuntimeError(f"Error downloading font from URL {font_url}")

        await proc.wait()
        log.debug("Downloaded theme fonts")

    except Exception as e:
        raise HyperglassError(str(e))


async def _render_theme():
    """Render Jinja2 template to Sass file."""
    log.debug("Rendering theme elements...")
    try:
        template = JINJA_ENV.get_template("templates/theme.sass.j2")
        rendered_theme = await template.render_async(params.branding)

        log.debug(f"Branding variables:\n{params.branding.json(indent=4)}")
        log.debug(f"Rendered theme:\n{str(rendered_theme)}")

        async with AIOFile(THEME_FILE, "w+") as file:
            await file.write(rendered_theme)
            await file.fsync()
        log.debug("Rendered theme elements")
    except Exception as e:
        raise HyperglassError(f"Error rendering theme: {e}")


async def _build_assets():
    """Build, bundle, and minify Sass/CSS/JS web assets."""
    log.debug("Building web assets...")

    yarn_command = "yarn --silent --emoji false --json --no-progress build"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=yarn_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=STATIC_DIR,
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
        log.debug(f'Built web assets with script {output_out["data"]}')
    except Exception as e:
        raise HyperglassError(str(e))


async def _render_all():
    """Run all asset rendering/building functions.

    Raises:
        HyperglassError: Raised if any downstream errors occur.
    """
    try:
        await _render_frontend_config()
        await _get_fonts()
        await _render_theme()
        await _build_assets()
    except HyperglassError as e:
        raise HyperglassError(str(e)) from None


def render_assets():
    """Render assets."""
    start = time.time()

    asyncio.run(_render_all())

    end = time.time()
    elapsed = round(end - start, 2)
    log.debug(f"Rendered assets in {elapsed} seconds.")
