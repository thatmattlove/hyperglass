"""hyperglass is a modern, customizable network looking glass written in Python 3.

https://github.com/checktheroads/hyperglass

The Clear BSD License

Copyright (c) 2020 Matthew Love
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted (subject to the limitations in the disclaimer
below) provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holder nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

# Standard Library
import os
import sys
import getpass
from pathlib import Path

# Third Party
import uvloop

# Project
from hyperglass.constants import METADATA

try:
    import stackprinter
except ImportError:
    pass
else:
    if sys.stdout.isatty():
        _style = "darkbg2"
    else:
        _style = "plaintext"
    stackprinter.set_excepthook(style=_style)

config_path = None

_CONFIG_PATHS = (Path.home() / "hyperglass", Path("/etc/hyperglass/"))

for path in _CONFIG_PATHS:
    try:
        if not isinstance(path, Path):
            path = Path(path)

        if path.exists():
            tmp = path / "test.tmp"
            tmp.touch()
            if tmp.exists():
                config_path = path
                tmp.unlink()
                break
    except Exception:
        config_path = None

if config_path is None:
    raise RuntimeError(
        """
No configuration directories were determined to both exist and be readable
by hyperglass. hyperglass is running as user '{un}' (UID '{uid}'), and tried to access
the following directories:
{dir}""".format(
            un=getpass.getuser(),
            uid=os.getuid(),
            dir="\n".join([" - " + str(p) for p in _CONFIG_PATHS]),
        )
    )

os.environ["hyperglass_directory"] = str(config_path)

uvloop.install()

__name__, __version__, __author__, __copyright__, __license__ = METADATA
