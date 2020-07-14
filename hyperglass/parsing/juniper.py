"""Parse Juniper XML Response to Structured Data."""

# Standard Library
from typing import Dict, Iterable

# Third Party
import xmltodict
from pydantic import ValidationError

# Project
from hyperglass.log import log
from hyperglass.util import validation_error_message
from hyperglass.exceptions import ParsingError, ResponseEmpty
from hyperglass.configuration import params
from hyperglass.parsing.models.juniper import JuniperRoute


def parse_juniper(output: Iterable) -> Dict:  # noqa: C901
    """Parse a Juniper BGP XML response."""
    data = {}

    for i, response in enumerate(output):
        try:
            parsed = xmltodict.parse(
                response, force_list=("rt", "rt-entry", "community", "nh")
            )

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
            raise ParsingError("Error parsing response data")

        except KeyError as err:
            log.critical(f"'{str(err)}' was not found in the response")
            raise ParsingError("Error parsing response data")

        except ValidationError as err:
            log.critical(str(err))
            raise ParsingError(validation_error_message(*err.errors()))

    return data
