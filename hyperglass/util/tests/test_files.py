"""Test file-related utilities."""

# Standard Library
import tempfile
from pathlib import Path

# Third Party
import pytest

# Local
from ..files import dotenv_to_dict

ENV_TEST = """KEY1=VALUE1
KEY2=VALUE2
KEY3=VALUE3
    """


def test_dotenv_to_dict_string():
    result = dotenv_to_dict(ENV_TEST)
    assert result.get("KEY1") == "VALUE1"
    assert result.get("KEY2") == "VALUE2"
    assert result.get("KEY3") == "VALUE3"


def test_dotenv_to_dict_file():
    _, filename = tempfile.mkstemp()
    file = Path(filename)
    with file.open("w+") as f:
        f.write(ENV_TEST)
    result = dotenv_to_dict(file)
    assert result.get("KEY1") == "VALUE1"
    assert result.get("KEY2") == "VALUE2"
    assert result.get("KEY3") == "VALUE3"
    file.unlink()


def test_dotenv_to_dict_raises_type_error():
    with pytest.raises(TypeError):
        dotenv_to_dict(True)


def test_dotenv_to_dict_raises_filenotfounderror():
    with pytest.raises(FileNotFoundError):
        dotenv_to_dict(Path("/tmp/not-a-thing"))  # noqa: S108


def test_dotenv_invalid_format():
    with pytest.raises(TypeError):
        dotenv_to_dict("this should raise an error")
