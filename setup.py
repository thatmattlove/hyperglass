# Standard Library Imports
import sys
from distutils.core import setup

if sys.version_info < (3, 6):
    sys.exit("Python 3.6+ is required.")


with open("README.md", "r") as ld:
    long_description = ld.read()

with open("requirements.txt", "r") as req:
    requirements = req.read().split("\n")

desc = "hyperglass is a modern, customizable network looking glass written in Python 3."

setup(
    name="hyperglass",
    version="1.0.0",
    author="Matt Love",
    author_email="matt@hyperglass.io",
    description=desc,
    url="https://github.com/checktheroads/hyperglass",
    python_requires=">=3.6",
    packages=["hyperglass"],
    install_requires=requirements,
    license="BSD 3-Clause Clear License",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
