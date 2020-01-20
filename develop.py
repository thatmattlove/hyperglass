"""Devloper functions."""

# Standard Library Imports
import os


def count_lines(directory):
    """Count lines of code.

    Arguments:
        directory {str} -- Path to count

    Returns:
        {int} -- Line count
    """
    lines = 0
    excluded = ("\n",)
    for thing in os.listdir(directory):
        thing = os.path.join(directory, thing)
        if os.path.isfile(thing):
            if thing.endswith(".py"):
                with open(thing, "r") as f:
                    readlines = [
                        line
                        for line in f.readlines()
                        if line not in excluded and not line.startswith("#")
                    ]
                    lines += len(readlines)

    for thing in os.listdir(directory):
        thing = os.path.join(directory, thing)
        if os.path.isdir(thing):
            lines += count_lines(thing)

    return lines
