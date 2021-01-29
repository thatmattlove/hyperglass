"""Utilities for working with files."""

# Standard Library
import shutil
from queue import Queue
from typing import List, Tuple, Union, Iterable, Optional, Generator
from pathlib import Path
from threading import Thread

# Project
from hyperglass.log import log


async def move_files(  # noqa: C901
    src: Path, dst: Path, files: Iterable[Path]
) -> Tuple[str]:
    """Move iterable of files from source to destination.

    Arguments:
        src {Path} -- Current directory of files
        dst {Path} -- Target destination directory
        files {Iterable} -- Iterable of files
    """

    def error(*args, **kwargs):
        msg = ", ".join(args)
        kwargs = {k: str(v) for k, v in kwargs.items()}
        error_msg = msg.format(**kwargs)
        log.error(error_msg)
        return RuntimeError(error_msg)

    if not isinstance(src, Path):
        try:
            src = Path(src)
        except TypeError:
            raise error("{p} is not a valid path", p=src)

    if not isinstance(dst, Path):
        try:
            dst = Path(dst)
        except TypeError:
            raise error("{p} is not a valid path", p=dst)

    if not isinstance(files, (List, Tuple, Generator)):
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
            raise error("Failed to migrate {f}: {e}", f=dst_file, e=e)

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


def copyfiles(src_files: Iterable[Path], dst_files: Iterable[Path]):
    """Copy iterable of files from source to destination with threading."""
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

    for i, file in enumerate(src_files):
        file_thread = FileCopy(src=file, dst=dst_files[i], queue=queue)
        threads += (file_thread,)

    for thread in threads:
        thread.start()

    for _file in src_files:
        copied = queue.get()
        log.debug("Copied {}", str(copied))

    for thread in threads:
        thread.join()

    for i, file in enumerate(dst_files):
        if not file.exists():
            raise RuntimeError("{} was not copied to {}", str(src_files[i]), str(file))

    return True


def check_path(
    path: Union[Path, str], mode: str = "r", create: bool = False
) -> Optional[Path]:
    """Verify if a path exists and is accessible."""

    result = None

    try:
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
            with path.open(mode):
                result = path

    except Exception:  # noqa: S110
        pass

    return result
