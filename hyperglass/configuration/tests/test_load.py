"""Test configuration file collection."""

# Standard Library
import tempfile
from pathlib import Path

# Project
from hyperglass.settings import Settings

# Local
from ..load import load_config

TOML = """
test = "from toml"
"""

YAML = """
test: from yaml
"""

JSON = """
{"test": "from json"}
"""

PY_VARIABLE = """
MAIN = {'test': 'from python variable'}
"""

PY_FUNCTION = """
def main():
    return {'test': 'from python function'}
"""

PY_COROUTINE = """
async def main():
    return {'test': 'from python coroutine'}
"""

CASES = (
    ("test.toml", "from toml", TOML),
    ("test.yaml", "from yaml", YAML),
    ("test_py_variable.py", "from python variable", PY_VARIABLE),
    ("test_py_function.py", "from python function", PY_FUNCTION),
    ("test_py_coroutine.py", "from python coroutine", PY_COROUTINE),
)


def test_collect(monkeypatch):
    with tempfile.TemporaryDirectory() as directory_name:
        directory = Path(directory_name)
        monkeypatch.setattr(Settings, "app_path", directory)
        for name, value, data in CASES:
            path = directory / Path(name)
            with path.open("w") as p:
                p.write(data)
            loaded = load_config(path.stem, required=True)
            assert loaded.get("test") is not None
            assert loaded["test"] == value
