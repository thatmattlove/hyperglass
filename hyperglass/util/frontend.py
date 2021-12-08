"""Utility functions for frontend-related tasks."""

# Standard Library
import os
import json
import math
import shutil
import typing as t
import asyncio
import subprocess
from pathlib import Path

# Project
from hyperglass.log import log

# Local
from .files import copyfiles, check_path, dotenv_to_dict

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.ui import UIParameters


def get_node_version() -> t.Tuple[int, int, int]:
    """Get the system's NodeJS version."""
    node_path = shutil.which("node")

    raw_version = subprocess.check_output([node_path, "--version"]).decode()  # noqa: S603

    # Node returns the version as 'v14.5.0', for example. Remove the v.
    version = raw_version.replace("v", "")
    # Parse the version parts.
    return tuple((int(v) for v in version.split(".")))


def get_ui_build_timeout() -> t.Optional[int]:
    """Read the UI build timeout from environment variables or set a default."""
    timeout = None

    if "HYPERGLASS_UI_BUILD_TIMEOUT" in os.environ:
        timeout = int(os.environ["HYPERGLASS_UI_BUILD_TIMEOUT"])
        log.info("Found UI build timeout environment variable: {}", timeout)

    elif "POETRY_HYPERGLASS_UI_BUILD_TIMEOUT" in os.environ:
        timeout = int(os.environ["POETRY_HYPERGLASS_UI_BUILD_TIMEOUT"])
        log.info("Found UI build timeout environment variable: {}", timeout)

    return timeout


async def check_node_modules() -> bool:
    """Check if node_modules exists and has contents."""

    ui_path = Path(__file__).parent.parent / "ui"
    node_modules = ui_path / "node_modules"

    exists = node_modules.exists()
    valid = exists

    if exists and not tuple(node_modules.iterdir()):
        valid = False

    return valid


async def read_package_json() -> t.Dict[str, t.Any]:
    """Import package.json as a python dict."""

    package_json_file = Path(__file__).parent.parent / "ui" / "package.json"

    try:

        with package_json_file.open("r") as file:
            package_json = json.load(file)

    except Exception as e:
        raise RuntimeError(f"Error reading package.json: {str(e)}")

    log.debug("package.json:\n{p}", p=package_json)

    return package_json


async def node_initial(timeout: int = 180, dev_mode: bool = False) -> str:
    """Initialize node_modules."""

    ui_path = Path(__file__).parent.parent / "ui"

    env_timeout = get_ui_build_timeout()

    if env_timeout is not None and env_timeout > timeout:
        timeout = env_timeout

    all_messages = ()

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd="yarn --silent --emoji false",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ui_path,
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        messages = stdout.decode("utf-8").strip()
        errors = stderr.decode("utf-8").strip()

        if proc.returncode != 0:
            raise RuntimeError(f"\nMessages:\n{messages}\nErrors:\n{errors}")

        await proc.wait()
        all_messages += (messages,)

    except Exception as e:
        raise RuntimeError(str(e))

    return "\n".join(all_messages)


async def build_ui(app_path: Path):
    """Execute `next build` & `next export` from UI directory.

    Raises:
        RuntimeError: Raised if exit code is not 0.
        RuntimeError: Raised when any other error occurs.
    """
    timeout = get_ui_build_timeout()

    ui_dir = Path(__file__).parent.parent / "ui"
    build_dir = app_path / "static" / "ui"

    build_command = "node_modules/.bin/next build"
    export_command = "node_modules/.bin/next export -o {f}".format(f=build_dir)

    all_messages = []
    for command in (build_command, export_command):
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd=command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ui_dir,
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            messages = stdout.decode("utf-8").strip()
            errors = stderr.decode("utf-8").strip()

            if proc.returncode != 0:
                raise RuntimeError(f"\nMessages:\n{messages}\nErrors:\n{errors}")

            await proc.wait()
            all_messages.append(messages)

        except asyncio.TimeoutError:
            raise RuntimeError(f"{timeout} second timeout exceeded while building UI")

        except Exception as err:
            log.error(err)
            raise RuntimeError(str(err))

    return "\n".join(all_messages)


def generate_opengraph(
    image_path: Path,
    max_width: int,
    max_height: int,
    target_path: Path,
    background_color: str,
):
    """Generate an OpenGraph compliant image."""
    # Third Party
    from PIL import Image

    def center_point(background: Image, foreground: Image):
        """Generate a tuple of center points for PIL."""
        bg_x, bg_y = background.size[0:2]
        fg_x, fg_y = foreground.size[0:2]
        x1 = math.floor((bg_x / 2) - (fg_x / 2))
        y1 = math.floor((bg_y / 2) - (fg_y / 2))
        x2 = math.floor((bg_x / 2) + (fg_x / 2))
        y2 = math.floor((bg_y / 2) + (fg_y / 2))
        return (x1, y1, x2, y2)

    # Convert image to JPEG format with static name "opengraph.jpg"
    dst_path = target_path / "opengraph.jpg"

    # Copy the original image to the target path
    copied = shutil.copy2(image_path, target_path)
    log.debug("Copied {} to {}", str(image_path), str(target_path))

    with Image.open(copied) as src:

        # Only resize the image if it needs to be resized
        if src.size[0] != max_width or src.size[1] != max_height:

            # Resize image while maintaining aspect ratio
            log.debug("Opengraph image is not 1200x630, resizing...")
            src.thumbnail((max_width, max_height))

        # Only impose a background image if the original image has
        # alpha/transparency channels
        if src.mode in ("RGBA", "LA"):
            log.debug("Opengraph image has transparency, converting...")
            background = Image.new("RGB", (max_width, max_height), background_color)
            background.paste(src, box=center_point(background, src))
            dst = background
        else:
            dst = src

        # Save new image to derived target path
        dst.save(dst_path)

        # Delete the copied image
        Path(copied).unlink()

        if not dst_path.exists():
            raise RuntimeError(f"Unable to save resized image to {str(dst_path)}")

        log.debug("Opengraph image ready at {}", str(dst_path))

    return True


def migrate_images(app_path: Path, params: "UIParameters"):
    """Migrate images from source code to install directory."""
    images_dir = app_path / "static" / "images"
    favicon_dir = images_dir / "favicons"
    check_path(favicon_dir, create=True)
    src_files = ()
    dst_files = ()

    for image in ("light", "dark", "favicon"):
        src: Path = getattr(params.web.logo, image)
        dst = images_dir / f"{image + src.suffix}"
        src_files += (src,)
        dst_files += (dst,)
    return copyfiles(src_files, dst_files)


def write_favicon_formats(formats: t.Tuple[t.Dict[str, t.Any]]) -> None:
    """Create a TypeScript file in the `ui` directory containing favicon formats.

    This file should stay the same, unless the favicons library updates
    supported formats.
    """
    # Standard Library
    from collections import OrderedDict

    file = Path(__file__).parent.parent / "ui" / "favicon-formats.ts"

    # Sort each favicon definition to ensure the result stays the same
    # time the UI build runs.
    ordered = json.dumps([OrderedDict(sorted(fmt.items())) for fmt in formats])
    data = "import type {{ Favicon }} from '~/types';export default {} as Favicon[];".format(
        ordered
    )
    file.write_text(data)


async def build_frontend(  # noqa: C901
    dev_mode: bool,
    dev_url: str,
    prod_url: str,
    params: "UIParameters",
    app_path: Path,
    force: bool = False,
    timeout: int = 180,
    full: bool = False,
) -> bool:
    """Perform full frontend UI build process."""
    # Standard Library
    import hashlib

    # Third Party
    from favicons import Favicons  # type:ignore

    # Project
    from hyperglass.constants import __version__

    # Create temporary file. json file extension is added for easy
    # webpack JSON parsing.
    dot_env_file = Path(__file__).parent.parent / "ui" / ".env"
    env_config = {}

    package_json = await read_package_json()

    # Set NextJS production/development mode and base URL based on
    # developer_mode setting.
    if dev_mode:
        env_config.update({"HYPERGLASS_URL": dev_url, "NODE_ENV": "development"})

    else:
        env_config.update({"HYPERGLASS_URL": prod_url, "NODE_ENV": "production"})

    # Check if hyperglass/ui/node_modules has been initialized. If not,
    # initialize it.
    initialized = await check_node_modules()

    if initialized:
        log.debug("node_modules is already initialized")

    elif not initialized:
        log.debug("node_modules has not been initialized. Starting initialization...")

        node_setup = await node_initial(timeout, dev_mode)

        if node_setup == "":
            log.debug("Re-initialized node_modules")

    images_dir = app_path / "static" / "images"
    favicon_dir = images_dir / "favicons"

    if not favicon_dir.exists():
        favicon_dir.mkdir()

    async with Favicons(
        source=params.web.logo.favicon,
        output_directory=favicon_dir,
        base_url="/images/favicons/",
    ) as favicons:
        await favicons.generate()
        log.debug("Generated {} favicons", favicons.completed)
        write_favicon_formats(favicons.formats())

    build_data = {
        "params": params.export_dict(),
        "version": __version__,
        "package_json": package_json,
    }

    build_json = json.dumps(build_data, default=str)

    # Create SHA256 hash from all parameters passed to UI, use as
    # build identifier.
    build_id = hashlib.sha256(build_json.encode()).hexdigest()

    # Read hard-coded environment file from last build. If build ID
    # matches this build's ID, don't run a new build.
    if dot_env_file.exists() and not force:
        env_data = dotenv_to_dict(dot_env_file)
        env_build_id = env_data.get("HYPERGLASS_BUILD_ID", "None")
        log.debug("Previous Build ID: {!r}", env_build_id)

        if env_build_id == build_id:
            log.debug("UI parameters unchanged since last build, skipping UI build...")
            return True

    env_config.update({"HYPERGLASS_BUILD_ID": build_id})

    dot_env_file.write_text("\n".join(f"{k}={v}" for k, v in env_config.items()))
    log.debug("Wrote UI environment file {!r}", str(dot_env_file))

    # Initiate Next.JS export process.
    if any((not dev_mode, force, full)):
        log.info("Starting UI build")
        initialize_result = await node_initial(timeout, dev_mode)
        build_result = await build_ui(app_path=app_path)

        if initialize_result:
            log.debug(initialize_result)
        elif initialize_result == "":
            log.debug("Re-initialized node_modules")

        if build_result:
            log.success("Completed UI build")
    elif dev_mode and not force:
        log.debug("Running in developer mode, did not build new UI files")

    migrate_images(app_path, params)

    generate_opengraph(
        params.web.opengraph.image,
        1200,
        630,
        images_dir,
        params.web.theme.colors.black,
    )

    return True
