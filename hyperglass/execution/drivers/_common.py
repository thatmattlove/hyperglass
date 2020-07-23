"""Base Connection Class."""

# Standard Library
from typing import Iterable

# Project
from hyperglass.log import log
from hyperglass.parsing.nos import nos_parsers
from hyperglass.parsing.common import parsers
from hyperglass.api.models.query import Query
from hyperglass.execution.construct import Construct
from hyperglass.configuration.models.routers import Router


class Connection:
    """Base transport driver class."""

    def __init__(self, device: Router, query_data: Query) -> None:
        """Initialize connection to device."""
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data.query_type
        self.query_target = self.query_data.query_target
        self._query = Construct(device=self.device, query_data=self.query_data)
        self.query = self._query.queries()

    async def parsed_response(self, output: Iterable) -> str:
        """Send output through common parsers."""

        log.debug(f"Pre-parsed responses:\n{output}")
        parsed = ()
        response = None

        nos_to_parse = nos_parsers.keys()
        query_types_to_parse = nos_parsers.get(self.device.nos, {}).keys()

        if not self.device.structured_output:
            for coro in parsers:
                for response in output:
                    _output = await coro(commands=self.query, output=response)
                    parsed += (_output,)
            response = "\n\n".join(parsed)
        elif (
            self.device.structured_output
            and self.device.nos in nos_to_parse
            and self.query_type not in query_types_to_parse
        ):
            for coro in parsers:
                for response in output:
                    _output = await coro(commands=self.query, output=response)
                    parsed += (_output,)
            response = "\n\n".join(parsed)
        elif (
            self.device.structured_output
            and self.device.nos in nos_to_parse
            and self.query_type in query_types_to_parse
        ):
            func = nos_parsers[self.device.nos][self.query_type]
            response = func(output)

        if response is None:
            response = "\n\n".join(output)

        log.debug(f"Post-parsed responses:\n{response}")
        return response
