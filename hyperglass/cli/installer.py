"""Install hyperglass."""

# Standard Library
import os
import shutil
from filecmp import dircmp
from pathlib import Path

# Third Party
import inquirer

# Local
from .echo import error, success, warning
from .util import create_dir

USER_PATH = Path.home() / "hyperglass"
ROOT_PATH = Path("/etc/hyperglass/")
ASSET_DIR = Path(__file__).parent.parent / "images"
IGNORED_FILES = [".DS_Store"]

INSTALL_PATHS = [
    inquirer.List(
        "install_path",
        message="Choose a directory for hyperglass",
        choices=[USER_PATH, ROOT_PATH],
    )
]


def prompt_for_path() -> str:
    """Recursively prompt the user for an app path until one is provided."""

    answer = inquirer.prompt(INSTALL_PATHS)

    if answer is None:
        warning("A directory for hyperglass is required")
        answer = prompt_for_path()

    return answer["install_path"]


class Installer:
    """Install hyperglass."""

    def __init__(self, unattended: bool):
        """Initialize installer."""

        self.unattended = unattended

    def install(self) -> None:
        """Complete the installation."""

        self.app_path = self._get_app_path()
        self._scaffold()
        self._migrate_static_assets()

    def _get_app_path(self) -> Path:
        """Find the app path from env variables or a prompt."""

        if self.unattended:
            return USER_PATH

        app_path = os.environ.get("HYPERGLASS_PATH", None)

        if app_path is None:
            app_path = prompt_for_path()

        return app_path

    def _scaffold(self) -> None:
        """Create the file structure necessary for hyperglass to run."""

        ui_dir = self.app_path / "static" / "ui"
        images_dir = self.app_path / "static" / "images"
        favicon_dir = images_dir / "favicons"
        custom_dir = self.app_path / "static" / "custom"

        create_dir(self.app_path)

        for path in (ui_dir, images_dir, favicon_dir, custom_dir):
            create_dir(path, parents=True)

    def _migrate_static_assets(self) -> bool:
        """Synchronize the project assets with the installation assets."""

        target_dir = self.app_path / "static" / "images"

        if not target_dir.exists():
            shutil.copytree(ASSET_DIR, target_dir)

        # Compare the contents of the project's asset directory (considered
        # the source of truth) with the installation directory. If they do
        # not match, delete the installation directory's asset directory and
        # re-copy it.
        compare_initial = dircmp(ASSET_DIR, target_dir, ignore=IGNORED_FILES)

        if not compare_initial.left_list == compare_initial.right_list:
            shutil.rmtree(target_dir)
            shutil.copytree(ASSET_DIR, target_dir)

            # Re-compare the source and destination directory contents to
            # ensure they match.
            compare_post = dircmp(ASSET_DIR, target_dir, ignore=IGNORED_FILES)

            if not compare_post.left_list == compare_post.right_list:
                error(
                    "Files in {a} do not match files in {b}",
                    a=str(ASSET_DIR),
                    b=str(target_dir),
                )
                return False

        success("Migrated assets from {a} to {b}", a=str(ASSET_DIR), b=str(target_dir))
        return True
