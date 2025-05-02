#!/usr/bin/env python3
"""Manage hyperglass version across multiple files."""

# Standard Library
import re
from typing import Tuple, Union, Pattern
from pathlib import Path

# Third Party
import typer

PACKAGE_JSON = Path(__file__).parent / "hyperglass" / "ui" / "package.json"
PACKAGE_JSON_PATTERN = re.compile(r"\s+\"version\"\:\s\"(.+)\"\,$")

PYPROJECT_TOML = Path(__file__).parent / "pyproject.toml"
PYPROJECT_PATTERN = re.compile(r"^version\s\=\s\"(.+)\"$")

CONSTANTS = Path(__file__).parent / "hyperglass" / "constants.py"
CONSTANT_PATTERN = re.compile(r"^__version__\s\=\s\"(.+)\"$")

UPGRADE_DOC = Path(__file__).parent / "docs" / "pages" / "installation" / "upgrading.mdx"
UPGRADE_DOC_PATTERN = re.compile(r"^git\scheckout\sv(.+)$")

UPGRADE_GH_FEATURE = Path(__file__).parent / ".github" / "ISSUE_TEMPLATE" / "1-feature-request.yaml"
UPGRADE_GH_FEATURE_PATTERN = re.compile(r"^[\s\t]+placeholder\:\sv(.+)$")

UPGRADE_GH_BUG = Path(__file__).parent / ".github" / "ISSUE_TEMPLATE" / "2-bug-report.yaml"

UPGRADE_GH_BUG_PATTERN = re.compile(r"^[\s\t]+placeholder\:\sv(.+)$")

UPGRADES = (
    ("package.json", PACKAGE_JSON, PACKAGE_JSON_PATTERN),
    ("pyproject.toml", PYPROJECT_TOML, PYPROJECT_PATTERN),
    ("constants.py", CONSTANTS, CONSTANT_PATTERN),
    ("upgrading.mdx", UPGRADE_DOC, UPGRADE_DOC_PATTERN),
    ("1-feature-request.yaml", UPGRADE_GH_FEATURE, UPGRADE_GH_FEATURE_PATTERN),
    ("2-bug-report.yaml", UPGRADE_GH_BUG, UPGRADE_GH_BUG_PATTERN),
)

cli = typer.Typer(name="version", no_args_is_help=True)


class Version:
    """Upgrade a file's version from one version to another."""

    new_version: Union[str, int]
    file: Path
    line_pattern: Pattern[str]
    old_version: Union[None, str, int] = None
    _did_check: bool = False
    _did_update: bool = False

    def __init__(
        self,
        *,
        name: str,
        new_version: Union[str, int],
        line_pattern: Union[Pattern, str],
        file: Union[Path, str],
    ) -> None:
        """Initialize version manager."""

        self.name = name
        self.new_version = new_version

        if isinstance(file, Path):
            self.file = file
        elif isinstance(file, str):
            self.file = Path(file)
        else:
            raise TypeError(f"'{repr(file)}' must be a string or Path object")

        if isinstance(line_pattern, Pattern):
            self.line_pattern = line_pattern
        elif isinstance(line_pattern, str):
            self.line_pattern = re.compile(line_pattern)
        else:
            raise TypeError(f"'{repr(line_pattern)}' is not a supported pattern")

    def __enter__(self) -> "Version":
        """Exit context manager for 0.01% better DX."""
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Exit context manager for 0.01% better DX."""
        pass

    def __str__(self) -> str:
        """Represent the state and/or action taken."""
        if self._did_update:
            old, new = self.upgrade_path
            return f"Upgraded {self.name} from {old} → {new}"
        if self._did_check:
            return f"No update required for {self.name} from version {self.old_version}"

        return f"{self.name} has not been checked"

    def upgrade(self) -> None:
        """Find a matching current version and upgrade it to the new version."""
        with self.file.open("r+") as file:
            found_match = False
            lines = file.readlines()
            self._did_check = True

            for idx, line in enumerate(lines):
                match = self.line_pattern.match(line)
                if match:
                    old_version = match.group(1).strip()
                    try:
                        old_version = int(old_version)
                    except ValueError:
                        # Old version can't be converted to an integer, which is fine.
                        pass
                    self.old_version = old_version

                    if self.old_version != self.new_version:
                        lines[idx] = re.sub(old_version, self.new_version, line)
                        found_match = True
                    break

            if found_match:
                file.seek(0)
                file.writelines(lines)
                file.truncate()
                self._did_update = True

    @property
    def upgrade_path(self) -> Tuple[Union[str, int], Union[str, int]]:
        """Get the old and new versions."""
        return (self.old_version, self.new_version)


def update_versions(new_version: str) -> None:
    """Update hyperglass version in all package files."""
    for name, file, pattern in UPGRADES:
        with Version(
            name=name,
            file=file,
            line_pattern=pattern,
            new_version=new_version,
        ) as version:
            version.upgrade()
            typer.echo(str(version))


if __name__ == "__main__":
    typer.run(update_versions)
