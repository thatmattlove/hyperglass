from distutils.core import setup

import sys

if sys.version_info < (3, 6):
    sys.exit("Python 3.6+ is required.")

import shutil
from pathlib import Path

with open("README.md", "r") as ld:
    long_description = ld.read()

package_json = {
    "dependencies": {
        "animsition": "^4.0.2",
        "clipboard": "^2.0.4",
        "fomantic-ui": "^2.7.7",
        "jquery": "^3.4.1",
    }
}

setup(
    name="hyperglass",
    version="1.0.0",
    author="Matt Love",
    author_email="matt@allroads.io",
    description="hyperglass is a modern, customizable network looking glass written in Python 3.",
    url="https://github.com/checktheroads/hyperglass",
    python_requires=">=3.6",
    packages=["hyperglass"],
    install_requires=[
        "aredis==1.1.5",
        "click==6.7",
        "hiredis==1.0.0",
        "http3==0.6.7",
        "jinja2==2.10.1",
        "libsass==0.18.0",
        "logzero==1.5.0",
        "markdown2==2.3.7",
        "netmiko==2.3.3",
        "passlib==1.7.1",
        "prometheus_client==0.7.0",
        "pydantic==0.29",
        "pyyaml==5.1.1",
        "redis==3.2.1",
        "sanic_limiter==0.1.3",
        "sanic==19.6.2",
        "sshtunnel==0.1.5",
    ],
    setup_requires=[
        "calmjs==3.4.1",
    ]
    package_json=package_json,
    license="BSD 3-Clause Clear License",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
