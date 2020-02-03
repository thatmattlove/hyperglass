"""Validate, construct, execute queries.

Constructs SSH commands or API call parameters based on front end
input, executes the commands/calls, returns the output to front end.
"""

# Project
# flake8: noqa: F401
from hyperglass.execution import execute, construct
