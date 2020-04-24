"""Parse Juniper XML Response to Structured Data."""

# Third Party
import xmltodict

# Project
from hyperglass.log import log
from hyperglass.exceptions import ParsingError
from hyperglass.parsing.models.juniper import JuniperRoute


def parse_juniper(output):
    """Parse a Juniper BGP XML response."""
    try:
        parsed = xmltodict.parse(output)["rpc-reply"]["route-information"][
            "route-table"
        ]
        validated = JuniperRoute(**parsed)
        return validated.serialize().export_dict()
    except xmltodict.expat.ExpatError as err:
        log.critical(str(err))
        raise ParsingError("Error parsing response data")
    except KeyError as err:
        log.critical(f"'{str(err)}' was not found in the response")
        raise ParsingError("Error parsing response data")
