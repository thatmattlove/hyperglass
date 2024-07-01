"""Coerce a Juniper route table in XML format to a standard BGP Table structure."""

# Standard Library
import re
from typing import TYPE_CHECKING, List, Sequence, Generator

# Third Party
import xmltodict  # type: ignore
from pydantic import PrivateAttr, ValidationError

# Project
from hyperglass.log import log
from hyperglass.exceptions.private import ParsingError
from hyperglass.models.parsing.juniper import JuniperBGPTable

# Local
from .._output import OutputPlugin

if TYPE_CHECKING:
    # Standard Library
    from collections import OrderedDict

    # Project
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query

    # Local
    from .._output import OutputType


REMOVE_PATTERNS = (
    # The XML response can a CLI banner appended to the end of the XML
    # string. For example:
    # ```
    # <rpc-reply>
    # ...
    # <cli>
    #   <banner>{master}</banner>
    # </cli>
    # </rpc-reply>
    #
    # {master} noqa: E800
    # ```
    #
    # This pattern will remove anything inside braces, including the braces.
    r"\{.+\}",
)


def clean_xml_output(output: str) -> str:
    """Remove Juniper-specific patterns from output."""

    def scrub(lines: List[str]) -> Generator[str, None, None]:
        """Clean & remove each pattern from each line."""
        for pattern in REMOVE_PATTERNS:
            for line in lines:
                # Remove the pattern & strip extra newlines
                scrubbed = re.sub(pattern, "", line.strip())
                # Only return non-empty and non-newline lines
                if scrubbed and scrubbed != "\n":
                    yield scrubbed

    lines = scrub(output.splitlines())

    return "\n".join(lines)


def parse_juniper(output: Sequence[str]) -> "OutputDataModel":  # noqa: C901
    """Parse a Juniper BGP XML response."""
    result = None

    _log = log.bind(plugin=BGPRoutePluginJuniper.__name__)
    for response in output:
        cleaned = clean_xml_output(response)

        try:
            parsed: "OrderedDict" = xmltodict.parse(
                cleaned, force_list=("rt", "rt-entry", "community")
            )
            if "rpc-reply" in parsed.keys():
                if "xnm:error" in parsed["rpc-reply"]:
                    if "message" in parsed["rpc-reply"]["xnm:error"]:
                        err = parsed["rpc-reply"]["xnm:error"]["message"]
                        raise ParsingError('Error from device: "{}"', err)

                parsed_base = parsed["rpc-reply"]["route-information"]
            elif "route-information" in parsed.keys():
                parsed_base = parsed["route-information"]

            if "route-table" not in parsed_base:
                return result

            if "rt" not in parsed_base["route-table"]:
                return result

            parsed = parsed_base["route-table"]
            validated = JuniperBGPTable(**parsed)
            bgp_table = validated.bgp_table()

            if result is None:
                result = bgp_table
            else:
                result += bgp_table

        except xmltodict.expat.ExpatError as err:
            _log.bind(error=str(err)).critical("Failed to decode XML")
            raise ParsingError("Error parsing response data") from err

        except KeyError as err:
            _log.bind(key=str(err)).critical("Missing required key in response")
            raise ParsingError("{key} was not found in the response", key=str(err)) from err

        except ValidationError as err:
            _log.critical(err)
            raise ParsingError(err) from err

    return result


class BGPRoutePluginJuniper(OutputPlugin):
    """Coerce a Juniper route table in XML format to a standard BGP Table structure."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: Sequence[str] = ("juniper",)
    directives: Sequence[str] = (
        "__hyperglass_juniper_bgp_route_table__",
        "__hyperglass_juniper_bgp_aspath_table__",
        "__hyperglass_juniper_bgp_community_table__",
    )

    def process(self, *, output: "OutputType", query: "Query") -> "OutputType":
        """Parse Juniper response if data is a string (and is therefore unparsed)."""
        should_process = all(
            (
                isinstance(output, (list, tuple)),
                query.device.platform in self.platforms,
                query.device.structured_output is True,
                query.device.has_directives(*self.directives),
            )
        )
        if should_process:
            return parse_juniper(output)
        return output
