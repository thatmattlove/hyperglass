"""hyperglass setuptools."""

# Standard Library
import sys
from pathlib import Path
from configparser import ConfigParser
from distutils.core import setup

# Project
from hyperglass import meta

# Project metadata
__name__, __version__, __author__, __copyright__, __license__ = meta

# Path & file objects
root_dir = Path.cwd()
pipfile = root_dir / "Pipfile"
readme = root_dir / "README.md"

# Read Pipfile
config = ConfigParser()
config.read_file(pipfile.open("r"))

# Pipenv requirements
requirements = list(config["packages"].keys())
dev_requirements = list(config["dev-packages"].keys())

# Pipenv Python versions
_parsed_py_ver = tuple(config["requires"].values())[0]
python_version = tuple(int(i) for i in _parsed_py_ver.strip('"').split("."))
pretty_python_version = ".".join(python_version)

if sys.version_info < python_version:
    sys.exit(f"Python {pretty_python_version}+ is required.")

with readme.open("r") as ld:
    long_description = ld.read()

desc = "hyperglass is a modern, customizable network looking glass written in Python 3."

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    author_email="matt@hyperglass.io",
    description=desc,
    url="https://github.com/checktheroads/hyperglass",
    python_requires=f">={pretty_python_version}",
    packages=[__name__],
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    license=__license__,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
