"""Install hyperglass."""

# Standard Library
import os
import time
import shutil
import typing as t
import getpass
from types import TracebackType
from filecmp import dircmp
from pathlib import Path

# Third Party
import typer
from rich.progress import Progress

# Project
from hyperglass.util import compare_lists
from hyperglass.settings import Settings
from hyperglass.constants import __version__

# Local
from .echo import echo

ASSET_DIR = Path(__file__).parent.parent / "images"
IGNORED_FILES = [".DS_Store"]


class Installer:
    """Install hyperglass."""

    app_path: Path
    progress: Progress
    user: str
    assets: int

    def __init__(self):
        """Start hyperglass installer."""
        self.app_path = Settings.app_path
        self.progress: Progress = Progress(console=echo._console)
        self.user = getpass.getuser()
        self.assets = len([p for p in ASSET_DIR.iterdir() if p.name not in IGNORED_FILES])

    def install(self) -> None:
        """Initialize tasks and start installer."""
        permissions_task = self.progress.add_task("[bright purple]Checking System", total=2)
        scaffold_task = self.progress.add_task(
            "[bright blue]Creating Directory Structures", total=3
        )
        asset_task = self.progress.add_task(
            "[bright cyan]Migrating Static Assets", total=self.assets
        )
        ui_task = self.progress.add_task("[bright teal]Initialzing UI", total=1, start=False)

        self.progress.start()

        self.check_permissions(task_id=permissions_task)
        self.scaffold(task_id=scaffold_task)
        self.migrate_static_assets(task_id=asset_task)
        self.init_ui(task_id=ui_task)

    def __enter__(self) -> t.Callable[[], None]:
        """Initialize tasks."""
        self.progress.print(f"Starting hyperglass {__version__} setup")
        return self.install

    def __exit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]] = None,
        exc_value: t.Optional[BaseException] = None,
        exc_traceback: t.Optional[TracebackType] = None,
    ):
        """Print errors on exit."""
        self.progress.stop()
        if exc_type is not None:
            echo._console.print_exception(show_locals=True)
            raise typer.Exit(1)
        raise typer.Exit(0)

    def check_permissions(self, task_id: int) -> None:
        """Ensure the executing user has permissions to the app path."""
        read = os.access(self.app_path, os.R_OK)
        if not read:
            self.progress.print(
                f"User {self.user!r} does not have read access to {self.app_path!s}", style="error"
            )
            raise typer.Exit(1)

        self.progress.advance(task_id)
        time.sleep(0.4)

        write = os.access(self.app_path, os.W_OK)
        if not write:
            self.progress.print(
                f"User {self.user!r} does not have write access to {self.app_path!s}", style="error"
            )
            raise typer.Exit(1)
        self.progress.advance(task_id)

    def scaffold(self, task_id: int) -> None:
        """Create the file structure necessary for hyperglass to run."""

        if not self.app_path.exists():
            self.progress.print("Created {!s}".format(self.app_path), style="info")
            self.app_path.mkdir(parents=True)

        self.progress.print(f"hyperglass path is {self.app_path!s}", style="subtle")
        self.progress.advance(task_id)

        ui_dir = self.app_path / "static" / "ui"
        favicon_dir = self.app_path / "static" / "images" / "favicons"

        for path in (ui_dir, favicon_dir):
            if not path.exists():
                self.progress.print("Created {!s}".format(path), style="info")
                path.mkdir(parents=True)

            self.progress.advance(task_id)
            time.sleep(0.4)

    def migrate_static_assets(self, task_id: int) -> None:
        """Synchronize the project assets with the installation assets."""

        target_dir = self.app_path / "static" / "images"

        def copy_func(src: str, dst: str):
            time.sleep(self.assets / 10)

            exists = Path(dst).exists()
            if not exists:
                copied = shutil.copy2(src, dst)
                self.progress.print(f"Copied {copied!s}", style="info")
            self.progress.advance(task_id)
            return dst

        if not target_dir.exists():
            shutil.copytree(
                ASSET_DIR,
                target_dir,
                ignore=shutil.ignore_patterns(*IGNORED_FILES),
                copy_function=copy_func,
            )

        # Compare the contents of the project's asset directory (considered
        # the source of truth) with the installation directory. If they do
        # not match, delete the installation directory's asset directory and
        # re-copy it.
        compare_initial = dircmp(ASSET_DIR, target_dir, ignore=IGNORED_FILES)

        if not compare_lists(
            compare_initial.left_list,
            compare_initial.right_list,
            ignore=["hyperglass-opengraph.jpg"],
        ):
            shutil.rmtree(target_dir)
            shutil.copytree(
                ASSET_DIR,
                target_dir,
                copy_function=copy_func,
                ignore=shutil.ignore_patterns(*IGNORED_FILES),
            )

            # Re-compare the source and destination directory contents to
            # ensure they match.
            compare_post = dircmp(ASSET_DIR, target_dir, ignore=IGNORED_FILES)

            if not compare_lists(
                compare_post.left_list, compare_post.right_list, ignore=["hyperglass-opengraph.jpg"]
            ):
                echo.error("Files in {!s} do not match files in {!s}", ASSET_DIR, target_dir)
                raise typer.Exit(1)
        else:
            self.progress.update(task_id, completed=self.assets, refresh=True)

    def init_ui(self, task_id: int) -> None:
        """Initialize UI."""
        # Project
        from hyperglass.log import log

        # Local
        from .util import build_ui

        with self.progress.console.capture():
            log.disable("hyperglass")
            build_ui(timeout=180)
            log.enable("hyperglass")
        self.progress.advance(task_id)
