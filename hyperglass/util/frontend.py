"""Utility functions for frontend-related tasks."""

# Standard Library
import os
import json
import math
import shutil
import asyncio
import subprocess
from typing import Dict, Optional
from pathlib import Path

# Project
from hyperglass.log import log

# Local
from .files import copyfiles, check_path


def get_node_version() -> int:
    """Get the system's NodeJS version."""
    node_path = shutil.which("node")

    raw_version = subprocess.check_output(  # noqa: S603
        [node_path, "--version"]
    ).decode()

    # Node returns the version as 'v14.5.0', for example. Remove the v.
    version = raw_version.replace("v", "")
    # Parse the version parts.
    major, minor, patch = version.split(".")

    return int(major)


def get_ui_build_timeout() -> Optional[int]:
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


async def read_package_json() -> Dict:
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


async def build_ui(app_path):
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


def migrate_images(app_path: Path, params: dict):
    """Migrate images from source code to install directory."""
    images_dir = app_path / "static" / "images"
    favicon_dir = images_dir / "favicons"
    check_path(favicon_dir, create=True)
    src_files = ()
    dst_files = ()

    for image in ("light", "dark", "favicon"):
        src = Path(params["web"]["logo"][image])
        dst = images_dir / f"{image + src.suffix}"
        src_files += (src,)
        dst_files += (dst,)
    return copyfiles(src_files, dst_files)


async def build_frontend(  # noqa: C901
    dev_mode: bool,
    dev_url: str,
    prod_url: str,
    params: Dict,
    app_path: Path,
    force: bool = False,
    timeout: int = 180,
) -> bool:
    """Perform full frontend UI build process.

    Securely creates temporary file, writes frontend configuration
    parameters to file as JSON. Then writes the name of the temporary
    file to /tmp/hyperglass.env.json as {"configFile": <file_name> }.

    Webpack reads /tmp/hyperglass.env.json, loads the temporary file,
    and sets its contents to Node environment variables during the build
    process.

    After the build is successful, the temporary file is automatically
    closed during garbage collection.

    Arguments:
        dev_mode {bool} -- Development Mode
        dev_url {str} -- Development Mode URL
        prod_url {str} -- Production Mode URL
        params {dict} -- Frontend Config paramters

    Raises:
        RuntimeError: Raised if errors occur during build process.

    Returns:
        {bool} -- True if successful
    """
    # Standard Library
    import hashlib
    import tempfile

    # Third Party
    from favicons import Favicons

    # Project
    from hyperglass.constants import __version__

    env_file = Path("/tmp/hyperglass.env.json")  # noqa: S108

    package_json = await read_package_json()

    env_vars = {
        "_HYPERGLASS_CONFIG_": params,
        "_HYPERGLASS_VERSION_": __version__,
        "_HYPERGLASS_PACKAGE_JSON_": package_json,
        "_HYPERGLASS_APP_PATH_": str(app_path),
    }

    # Set NextJS production/development mode and base URL based on
    # developer_mode setting.
    if dev_mode:
        env_vars.update({"NODE_ENV": "development", "_HYPERGLASS_URL_": dev_url})

    else:
        env_vars.update({"NODE_ENV": "production", "_HYPERGLASS_URL_": prod_url})

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

    try:
        if not favicon_dir.exists():
            favicon_dir.mkdir()
        async with Favicons(
            source=params["web"]["logo"]["favicon"],
            output_directory=favicon_dir,
            base_url="/images/favicons/",
        ) as favicons:
            await favicons.generate()
            log.debug("Generated {} favicons", favicons.completed)
            env_vars.update({"_HYPERGLASS_FAVICONS_": favicons.formats()})

        env_json = json.dumps(env_vars, default=str)

        # Create SHA256 hash from all parameters passed to UI, use as
        # build identifier.
        build_id = hashlib.sha256(env_json.encode()).hexdigest()

        # Read hard-coded environment file from last build. If build ID
        # matches this build's ID, don't run a new build.
        if env_file.exists() and not force:

            with env_file.open("r") as ef:
                ef_id = json.load(ef).get("buildId", "empty")

                log.debug("Previous Build ID: {id}", id=ef_id)

            if ef_id == build_id:

                log.debug(
                    "UI parameters unchanged since last build, skipping UI build..."
                )

                return True

        # Create temporary file. json file extension is added for easy
        # webpack JSON parsing.
        temp_file = tempfile.NamedTemporaryFile(
            mode="w+", prefix="hyperglass_", suffix=".json", delete=not dev_mode
        )

        log.info("Starting UI build...")
        log.debug(
            f"Created temporary UI config file: '{temp_file.name}' for build {build_id}"
        )

        with Path(temp_file.name).open("w+") as temp:
            temp.write(env_json)

            # Write "permanent" file (hard-coded named) for Node to read.
            env_file.write_text(
                json.dumps({"configFile": temp_file.name, "buildId": build_id})
            )

            # While temporary file is still open, initiate UI build process.
            if not dev_mode or force:
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
            Path(params["web"]["opengraph"]["image"]),
            1200,
            630,
            images_dir,
            params["web"]["theme"]["colors"]["black"],
        )

    except Exception as err:
        log.error(err)
        raise RuntimeError(str(err)) from None

    return True
