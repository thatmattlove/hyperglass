"""Parse Juniper XML Response to Structured Data."""

# Standard Library
import re
from typing import Dict, List, Iterable, Generator

# Third Party
import xmltodict
from pydantic import ValidationError

# Project
from hyperglass.log import log
from hyperglass.exceptions import ParsingError, ResponseEmpty
from hyperglass.configuration import params
from hyperglass.models.parsing.juniper import JuniperRoute

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


def parse_juniper(output: Iterable) -> Dict:  # noqa: C901
    """Parse a Juniper BGP XML response."""
    data = {}

    for i, response in enumerate(output):
        cleaned = clean_xml_output(response)

        try:
            parsed = xmltodict.parse(
                cleaned, force_list=("rt", "rt-entry", "community")
            )

            log.debug("Initially Parsed Response: \n{}", parsed)

            if "rpc-reply" in parsed.keys():
                parsed_base = parsed["rpc-reply"]["route-information"]
            elif "route-information" in parsed.keys():
                parsed_base = parsed["route-information"]

            if "route-table" not in parsed_base:
                raise ResponseEmpty(params.messages.no_output)

            if "rt" not in parsed_base["route-table"]:
                raise ResponseEmpty(params.messages.no_output)

            parsed = parsed_base["route-table"]

            validated = JuniperRoute(**parsed)
            serialized = validated.serialize().export_dict()

            if i == 0:
                data.update(serialized)
            else:
                data["routes"].extend(serialized["routes"])

        except xmltodict.expat.ExpatError as err:
            log.critical(str(err))
            raise ParsingError("Error parsing response data") from err

        except KeyError as err:
            log.critical("{} was not found in the response", str(err))
            raise ParsingError("Error parsing response data")

        except ValidationError as err:
            log.critical(str(err))
            raise ParsingError(err.errors())

    return data
