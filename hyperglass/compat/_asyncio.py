"""Functions for maintaining asyncio compatability with other versions of Python."""

# Standard Library
import sys
import asyncio
import weakref

try:
    from asyncio import get_running_loop
except ImportError:
    from asyncio.events import _get_running_loop as get_running_loop

RUNNING_PYTHON_VERSION = sys.version_info

# _patch_loop, _patched_run, and _cancel_all_tasks are taken directly
# from github.com/nickdavis:
# https://gist.github.com/nickdavies/4a37c6cd9dcc7041fddd2d2a81cee383

# These functions are a backport of the functionality added in
# Python 3.7 to support asyncio.run(), which is used in several areas
# of hyperglass. Because the LTS version of Ubuntu at this time (18.04)
# still ships with Python 3.6, compatibility with Python 3.6 is the
# goal.


def _patch_loop(loop):
    tasks = weakref.WeakSet()

    task_factory = [None]

    def _set_task_factory(factory):
        task_factory[0] = factory

    def _get_task_factory():
        return task_factory[0]

    def _safe_task_factory(loop, coro):
        if task_factory[0] is None:
            task = asyncio.Task(coro, loop=loop)
            if task._source_traceback:
                del task._source_traceback[-1]
        else:
            task = task_factory[0](loop, coro)
        tasks.add(task)
        return task

    loop.set_task_factory(_safe_task_factory)
    loop.set_task_factory = _set_task_factory
    loop.get_task_factory = _get_task_factory

    return tasks


def _cancel_all_tasks(loop, tasks):
    to_cancel = [task for task in tasks if not task.done()]

    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True)
    )

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def _patched_run(main, *, debug=False):
    try:
        loop = get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        raise RuntimeError("asyncio.run() cannot be called from a running event loop")

    if not asyncio.iscoroutine(main):
        raise ValueError("a coroutine was expected, got {!r}".format(main))

    loop = asyncio.new_event_loop()
    tasks = _patch_loop(loop)

    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(main)
    finally:
        try:
            _cancel_all_tasks(loop, tasks)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()


# If local system's python version is at least 3.6, use the backported
# asyncio runner.
if RUNNING_PYTHON_VERSION >= (3, 6):
    aiorun = _patched_run

# If the local system's python version is at least 3.7, use the standard
# library's asyncio.run()
elif RUNNING_PYTHON_VERSION >= (3, 7):
    aiorun = asyncio.run
