"""Parse Arista JSON Response to Structured Data."""

# Standard Library
import json
import typing as t

# Third Party
from pydantic import PrivateAttr, ValidationError

# Project
from hyperglass.log import log
from hyperglass.exceptions.private import ParsingError
from hyperglass.models.parsing.arista_eos import AristaBGPTable

# Local
from .._output import OutputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query

    # Local
    from .._output import OutputType


def parse_arista(output: t.Sequence[str]) -> "OutputDataModel":
    """Parse a Arista BGP JSON response."""
    result = None

    _log = log.bind(plugin=BGPRoutePluginArista.__name__)

    for response in output:
        try:
            parsed: t.Dict = json.loads(response)

            _log.debug("Pre-parsed data", data=parsed)

            vrf = list(parsed["vrfs"].keys())[0]
            routes = parsed["vrfs"][vrf]

            validated = AristaBGPTable(**routes)
            bgp_table = validated.bgp_table()

            if result is None:
                result = bgp_table
            else:
                result += bgp_table

        except json.JSONDecodeError as err:
            _log.bind(error=str(err)).critical("Failed to decode JSON")
            raise ParsingError("Error parsing response data") from err

        except KeyError as err:
            _log.bind(key=str(err)).critical("Missing required key in response")
            raise ParsingError("Error parsing response data") from err

        except IndexError as err:
            _log.critical(err)
            raise ParsingError("Error parsing response data") from err

        except ValidationError as err:
            _log.critical(err)
            raise ParsingError(err.errors()) from err

    return result


class BGPRoutePluginArista(OutputPlugin):
    """Coerce a Arista route table in JSON format to a standard BGP Table structure."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("arista_eos",)
    directives: t.Sequence[str] = (
        "__hyperglass_arista_eos_bgp_route_table__",
        "__hyperglass_arista_eos_bgp_aspath_table__",
        "__hyperglass_arista_eos_bgp_community_table__",
    )

    def process(self, *, output: "OutputType", query: "Query") -> "OutputType":
        """Parse Arista response if data is a string (and is therefore unparsed)."""
        should_process = all(
            (
                isinstance(output, (list, tuple)),
                query.device.platform in self.platforms,
                query.device.structured_output is True,
                query.device.has_directives(*self.directives),
            )
        )
        if should_process:
            return parse_arista(output)
        return output
