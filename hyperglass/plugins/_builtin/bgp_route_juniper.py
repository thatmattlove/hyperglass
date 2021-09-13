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
    from hyperglass.models.config.devices import Device

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

    for response in output:
        cleaned = clean_xml_output(response)

        try:
            parsed: "OrderedDict" = xmltodict.parse(
                cleaned, force_list=("rt", "rt-entry", "community")
            )

            log.debug("Initially Parsed Response: \n{}", parsed)

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
            raise ParsingError("Error parsing response data") from err

        except KeyError as err:
            raise ParsingError("{key} was not found in the response", key=str(err))

        except ValidationError as err:
            raise ParsingError(err)

    return result


class BGPRoutePluginJuniper(OutputPlugin):
    """Coerce a Juniper route table in XML format to a standard BGP Table structure."""

    __hyperglass_builtin__: bool = PrivateAttr(True)

    def process(self, output: "OutputType", device: "Device") -> "OutputType":
        """Parse Juniper response if data is a string (and is therefore unparsed)."""
        if isinstance(output, (list, tuple)) and device.structured_output:
            return parse_juniper(output)
        return output
