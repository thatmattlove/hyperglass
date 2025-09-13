"""Coerce a MikroTik route table in text format to a standard BGP Table structure."""

# Standard Library
from typing import TYPE_CHECKING, Sequence, Union, List

# Third Party
from pydantic import PrivateAttr, ValidationError

# Project
from hyperglass.log import log
from hyperglass.exceptions.private import ParsingError
from hyperglass.models.parsing.mikrotik import MikrotikBGPTable

# Local
from .._output import OutputPlugin

if TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query
    from .._output import OutputType


def _normalize_output(output: Union[str, Sequence[str]]) -> List[str]:
    """Ensure the output is a list of strings."""
    if isinstance(output, str):
        return [output]
    return list(output)


def parse_mikrotik(output: Union[str, Sequence[str]]) -> "OutputDataModel":
    """Parse a MikroTik BGP text response."""
    result = None
    out_list = _normalize_output(output)

    _log = log.bind(plugin=BGPSTRRoutePluginMikrotik.__name__)
    combined_output = "\n".join(out_list)
    _log.debug(f"Combined output length: {len(combined_output)}")

    try:
        # Pass the entire combined output to the parser at once
        validated = MikrotikBGPTable.parse_text(combined_output)
        result = validated.bgp_table()
        _log.debug(f"Successfully parsed {len(validated.routes)} routes")

    except ValidationError as err:
        _log.critical(err)
        raise ParsingError(err) from err
    except Exception as err:
        _log.bind(error=str(err)).critical("Failed to parse MikroTik BGP output")
        raise ParsingError("Error parsing response data") from err

    return result


class BGPSTRRoutePluginMikrotik(OutputPlugin):
    """Coerce a MikroTik route table in text format to a standard BGP Table structure."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: Sequence[str] = ("mikrotik_routeros", "mikrotik_switchos", "mikrotik")

    directives: Sequence[str] = (
        "__hyperglass_mikrotik_bgp_route_table__",
        "__hyperglass_mikrotik_bgp_aspath_table__",
        "__hyperglass_mikrotik_bgp_community_table__",
    )

    def process(self, *, output: "OutputType", query: "Query") -> "OutputType":
        """Parse MikroTik response if data is text (and is therefore unparsed)."""
        _log = log.bind(plugin=self.__class__.__name__)
        _log.debug("Processing MikroTik output with structured parser")

        is_text = isinstance(output, (list, tuple, str))
        has_platform = query.device.platform in self.platforms
        wants_structured = bool(getattr(query.device, "structured_output", False))
        has_directives = query.device.has_directives(*self.directives)

        should_process = all((is_text, has_platform, wants_structured, has_directives))
        if not should_process:
            _log.debug(
                "Skipping structured parser: "
                f"is_text={is_text}, platform={query.device.platform!r} (o@k={has_platform}), "
                f"structured_output={wants_structured}, has_directives={has_directives}"
            )
            return output

        return parse_mikrotik(output)
