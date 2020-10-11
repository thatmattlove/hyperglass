"""Base Connection Class."""

# Standard Library
from typing import Iterable

# Project
from hyperglass.log import log
from hyperglass.models.api import Query
from hyperglass.parsing.nos import scrape_parsers, structured_parsers
from hyperglass.parsing.common import parsers
from hyperglass.models.config.devices import Device

# Local
from ._construct import Construct


class Connection:
    """Base transport driver class."""

    def __init__(self, device: Device, query_data: Query) -> None:
        """Initialize connection to device."""
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data.query_type
        self.query_target = self.query_data.query_target
        self._query = Construct(device=self.device, query_data=self.query_data)
        self.query = self._query.queries()

    async def parsed_response(  # noqa: C901 ("too complex")
        self, output: Iterable
    ) -> str:
        """Send output through common parsers."""

        log.debug("Pre-parsed responses:\n{}", output)
        parsed = ()
        response = None

        structured_nos = structured_parsers.keys()
        structured_query_types = structured_parsers.get(self.device.nos, {}).keys()

        scrape_nos = scrape_parsers.keys()
        scrape_query_types = scrape_parsers.get(self.device.nos, {}).keys()

        if not self.device.structured_output:
            _parsed = ()
            for func in parsers:
                for response in output:
                    _output = func(commands=self.query, output=response)
                    _parsed += (_output,)
            if self.device.nos in scrape_nos and self.query_type in scrape_query_types:
                func = scrape_parsers[self.device.nos][self.query_type]
                for response in _parsed:
                    _output = func(response)
                    parsed += (_output,)
            else:
                parsed += _parsed

            response = "\n\n".join(parsed)
        elif (
            self.device.structured_output
            and self.device.nos in structured_nos
            and self.query_type not in structured_query_types
        ):
            for func in parsers:
                for response in output:
                    _output = func(commands=self.query, output=response)
                    parsed += (_output,)
            response = "\n\n".join(parsed)
        elif (
            self.device.structured_output
            and self.device.nos in structured_nos
            and self.query_type in structured_query_types
        ):
            func = structured_parsers[self.device.nos][self.query_type]
            response = func(output)

        if response is None:
            response = "\n\n".join(output)

        log.debug("Post-parsed responses:\n{}", response)
        return response
