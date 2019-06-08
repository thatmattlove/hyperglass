# https://github.com/checktheroads/hyperglass
"""
Constructs SSH commands or API call parameters based on front end input, executes the
commands/calls, returns the output to front end
"""
from hyperglass.command import execute
from hyperglass.command import construct
from hyperglass.command import validate
