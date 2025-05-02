"""Test file-related utilities."""

# Standard Library
import string
import secrets
from pathlib import Path

# Third Party
import pytest

# Local
from ..files import copyfiles, check_path, move_files, dotenv_to_dict

ENV_TEST = """KEY1=VALUE1
KEY2=VALUE2
KEY3=VALUE3
    """


def _random_string(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    result = "".join(secrets.choice(alphabet) for i in range(length))
    return result


def test_dotenv_to_dict_string():
    result = dotenv_to_dict(ENV_TEST)
    assert result.get("KEY1") == "VALUE1"
    assert result.get("KEY2") == "VALUE2"
    assert result.get("KEY3") == "VALUE3"


def test_dotenv_to_dict_file(tmp_path_factory: pytest.TempPathFactory):
    dirname = tmp_path_factory.mktemp("dotenv")
    file_ = dirname / "test_dotenv_to_dict_file.env"
    with file_.open("w+") as f:
        f.write(ENV_TEST)
    result = dotenv_to_dict(file_)
    assert result.get("KEY1") == "VALUE1"
    assert result.get("KEY2") == "VALUE2"
    assert result.get("KEY3") == "VALUE3"


def test_dotenv_to_dict_raises_type_error():
    with pytest.raises(TypeError):
        dotenv_to_dict(True)


def test_dotenv_to_dict_raises_filenotfounderror():
    with pytest.raises(FileNotFoundError):
        dotenv_to_dict(Path("/tmp/not-a-thing"))  # noqa: S108


def test_dotenv_invalid_format():
    with pytest.raises(TypeError):
        dotenv_to_dict("this should raise an error")


def test_check_path_file(tmp_path_factory: pytest.TempPathFactory):
    dir_ = tmp_path_factory.mktemp("test")
    file_ = dir_ / "file.txt"
    file_.touch()
    result = check_path(file_)
    assert result == file_


def test_check_path_dir(tmp_path_factory: pytest.TempPathFactory):
    dir_ = tmp_path_factory.mktemp("test")
    child = dir_ / "child_dir"
    child.mkdir()
    result = check_path(child)
    assert child.exists()
    assert result == child


def test_check_path_create_file(tmp_path_factory: pytest.TempPathFactory):
    dir_ = tmp_path_factory.mktemp("test")
    file_ = dir_ / "file.txt"
    result = check_path(file_, create=True)
    assert file_.exists()
    assert result == file_


def test_check_path_create_dir(tmp_path_factory: pytest.TempPathFactory):
    dir_ = tmp_path_factory.mktemp("test")
    child = dir_ / "child_dir"
    result = check_path(child, create=True)
    assert child.exists()
    assert result == child


def test_check_path_raises(tmp_path_factory: pytest.TempPathFactory):
    dir_ = tmp_path_factory.mktemp("test")
    file_ = dir_ / "file.txt"
    with pytest.raises(FileNotFoundError):
        check_path(file_, create=False)


@pytest.mark.asyncio
async def test_move_files(tmp_path_factory: pytest.TempPathFactory):
    src = tmp_path_factory.mktemp("src")
    dst = tmp_path_factory.mktemp("dst")
    filenames = ("".join(_random_string(8)) for _ in range(10))
    files = [src / name for name in filenames]
    [f.touch() for f in files]
    result = await move_files(src, dst, files)
    dst_files = sorted([str(c) for c in dst.iterdir()])
    result_files = sorted(result)
    assert result_files == dst_files


@pytest.mark.asyncio
async def test_move_files_raise(tmp_path_factory: pytest.TempPathFactory):
    src = tmp_path_factory.mktemp("src")
    dst = tmp_path_factory.mktemp("dst")
    filenames = ("".join(_random_string(8)) for _ in range(10))
    files = [src / name for name in filenames]
    with pytest.raises(RuntimeError):
        await move_files(src, dst, files)


def test_copyfiles(tmp_path_factory: pytest.TempPathFactory):
    src = tmp_path_factory.mktemp("src")
    dst = tmp_path_factory.mktemp("dst")
    filenames = ["".join(_random_string(8)) for _ in range(10)]
    src_files = [src / name for name in filenames]
    dst_files = [dst / name for name in filenames]
    [f.touch() for f in src_files]
    result = copyfiles(src_files, dst_files)
    assert result


def test_copyfiles_wrong_length(tmp_path_factory: pytest.TempPathFactory):
    src = tmp_path_factory.mktemp("src")
    dst = tmp_path_factory.mktemp("dst")
    filenames = ["".join(_random_string(8)) for _ in range(10)]
    dst_filenames = filenames[1:8]
    src_files = [src / name for name in filenames]
    dst_files = [dst / name for name in dst_filenames]
    [f.touch() for f in src_files]
    with pytest.raises(ValueError):
        copyfiles(src_files, dst_files)
