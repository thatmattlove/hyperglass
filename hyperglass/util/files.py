"""Utilities for working with files."""

# Standard Library
import shutil
import typing as t
from queue import Queue
from pathlib import Path
from threading import Thread


async def move_files(src: Path, dst: Path, files: t.Iterable[Path]) -> t.Tuple[str]:  # noqa: C901
    """Move iterable of files from source to destination."""

    # Project
    from hyperglass.log import log

    def error(*args, **kwargs):
        msg = ", ".join(args)
        kwargs = {k: str(v) for k, v in kwargs.items()}
        error_msg = msg.format(**kwargs)
        log.error(error_msg)
        return RuntimeError(error_msg)

    if not isinstance(src, Path):
        try:
            src = Path(src)
        except TypeError as err:
            raise error("{p} is not a valid path", p=src) from err

    if not isinstance(dst, Path):
        try:
            dst = Path(dst)
        except TypeError as err:
            raise error("{p} is not a valid path", p=dst) from err

    if not isinstance(files, (t.List, t.Tuple, t.Generator)):
        raise error(
            "{fa} must be an iterable (list, tuple, or generator). Received {f}",
            fa="Files argument",
            f=files,
        )

    for path in (src, dst):
        if not path.exists():
            raise error("{p} does not exist", p=path)

    migrated = ()

    for file in files:
        dst_file = dst / file.name

        if not file.exists():
            raise error("{f} does not exist", f=file)

        try:
            if not dst_file.exists():
                shutil.copyfile(file, dst_file)
                migrated += (str(dst_file),)
        except Exception as e:
            raise error("Failed to migrate {f}: {e}", f=dst_file, e=e) from e

    return migrated


class FileCopy(Thread):
    """Custom thread for copyfiles() function."""

    def __init__(self, src: Path, dst: Path, queue: Queue):
        """Initialize custom thread."""
        super().__init__()

        if not src.exists():
            raise ValueError("{} does not exist", str(src))

        self.src = src
        self.dst = dst
        self.queue = queue

    def run(self):
        """Put one object into the queue for each file."""
        try:
            try:
                shutil.copy(self.src, self.dst)
            except IOError as err:
                self.queue.put(err)
            else:
                self.queue.put(self.src)
        finally:
            pass


def copyfiles(src_files: t.Iterable[Path], dst_files: t.Iterable[Path]):
    """Copy iterable of files from source to destination with threading."""

    # Project
    from hyperglass.log import log

    queue = Queue()
    threads = ()
    src_files_len = len(src_files)
    dst_files_len = len(dst_files)

    if src_files_len != dst_files_len:
        raise ValueError(
            "The number of source files "
            + "({}) must match the number of destination files ({}).".format(
                src_files_len, dst_files_len
            )
        )

    for i, file_ in enumerate(src_files):
        file_thread = FileCopy(src=file_, dst=dst_files[i], queue=queue)
        threads += (file_thread,)

    for thread in threads:
        thread.start()

    for _ in src_files:
        copied = queue.get()
        log.bind(path=copied).debug("Copied file", path=copied)

    for thread in threads:
        thread.join()

    for i, file_ in enumerate(dst_files):
        if not file_.exists():
            raise RuntimeError("{!s} was not copied to {!s}", src_files[i], file_)

    return True


def check_path(
    path: t.Union[Path, str], *, mode: str = "r", create: bool = False
) -> t.Optional[Path]:
    """Verify if a path exists and is accessible."""

    result = None

    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists():
        if create:
            if path.is_file():
                path.parent.mkdir(parents=True)
            else:
                path.mkdir(parents=True)
        else:
            raise FileNotFoundError(f"{str(path)} does not exist.")

    if path.exists():
        if path.is_file():
            with path.open(mode):
                result = path
        else:
            result = path

    return result


def dotenv_to_dict(dotenv: t.Union[Path, str]) -> t.Dict[str, str]:
    """Convert a .env file to a Python dict."""
    if not isinstance(dotenv, (Path, str)):
        raise TypeError("Argument 'file' must be a Path object or string")
    result = {}
    data = ""
    if isinstance(dotenv, Path):
        if not dotenv.exists():
            raise FileNotFoundError("{!r} does not exist", str(dotenv))
        with dotenv.open("r") as f:
            data = f.read()
    else:
        data = dotenv

    for line in (line for line in (line.strip() for line in data.splitlines()) if line):
        parts = line.split("=")
        if len(parts) != 2:
            raise TypeError(
                f"Line {line!r} is improperly formatted. "
                "Expected a key/value pair such as 'key=value'"
            )
        key, value = line.split("=")
        result[key.strip()] = value.strip()

    return result
