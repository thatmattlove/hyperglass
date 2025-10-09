"""Parse MikroTik traceroute output to structured data."""

# Standard Library
import typing as t

# Third Party
from pydantic import PrivateAttr, ValidationError

# Project
from hyperglass.log import log, log as _log
from hyperglass.settings import Settings
from hyperglass.exceptions.private import ParsingError
from hyperglass.models.parsing.mikrotik import MikrotikTracerouteTable
from hyperglass.state import use_state

# Local
from .._output import OutputPlugin

if t.TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query
    from .._output import OutputType


def _normalize_output(output: t.Union[str, t.Sequence[str]]) -> t.List[str]:
    """Ensure the output is a list of strings."""
    if isinstance(output, str):
        return [output]
    return list(output)


def _clean_traceroute_only(
    output: t.Union[str, t.Sequence[str]], query: "Query"
) -> t.Union[str, t.Tuple[str, ...]]:
    """Clean traceroute output using MikrotikGarbageOutput plugin."""
    from .mikrotik_garbage_output import MikrotikGarbageOutput

    out_list = _normalize_output(output)
    cleaner = MikrotikGarbageOutput()

    cleaned_list: t.List[str] = []
    for piece in out_list:
        try:
            cleaned_piece = cleaner._clean_traceroute_output(piece)
        except Exception:
            cleaned_piece = piece
        cleaned_list.append(cleaned_piece)

    if isinstance(output, str):
        return cleaned_list[0] if cleaned_list else ""
    return tuple(cleaned_list)


def parse_mikrotik_traceroute(
    output: t.Union[str, t.Sequence[str]], target: str, source: str
) -> "OutputDataModel":
    """Parse a cleaned MikroTik traceroute text response."""
    out_list = _normalize_output(output)
    _log = log.bind(plugin=TraceroutePluginMikrotik.__name__)
    combined_output = "\n".join(out_list)

    if Settings.debug:
        _log.debug(
            "Parsing cleaned traceroute input",
            target=target,
            source=source,
            pieces=len(out_list),
            combined_len=len(combined_output),
        )

    try:
        validated = MikrotikTracerouteTable.parse_text(combined_output, target, source)
        result = validated.traceroute_result()
        result.raw_output = combined_output

        if Settings.debug:
            _log.debug(
                "Parsed traceroute result",
                hops=len(validated.hops),
                target=result.target,
                source=result.source,
            )

    except ValidationError as err:
        _log.critical(err)
        raise ParsingError(err) from err
    except Exception as err:
        _log.bind(error=str(err)).critical("Failed to parse MikroTik traceroute output")
        raise ParsingError("Error parsing traceroute response data") from err

    return result


class TraceroutePluginMikrotik(OutputPlugin):
    """Convert MikroTik traceroute output to structured format."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("mikrotik_routeros", "mikrotik_switchos", "mikrotik")
    directives: t.Sequence[str] = ("__hyperglass_mikrotik_traceroute__",)

    def process(self, *, output: "OutputType", query: "Query") -> "OutputDataModel":
        """Process the MikroTik traceroute output."""
        target = getattr(query, "target", "unknown")
        source = getattr(query, "source", "unknown")

        if hasattr(query, "query_target") and query.query_target:
            target = str(query.query_target)

        if hasattr(query, "device") and query.device:
            source = getattr(query.device, "name", source)

        _log = log.bind(plugin=TraceroutePluginMikrotik.__name__)

        # Log raw router output only when debug is enabled
        if Settings.debug:
            try:
                if isinstance(output, (tuple, list)):
                    try:
                        combined_raw = "\n".join(output)
                    except Exception:
                        combined_raw = repr(output)
                else:
                    combined_raw = output if isinstance(output, str) else repr(output)

                _log.debug("Router raw output:\n{}", combined_raw)
            except Exception:
                _log.exception("Failed to log router raw output")

        try:
            params = use_state("params")
        except Exception:
            params = None

        device = getattr(query, "device", None)

        # Check if structured output is enabled
        if device is None:
            if Settings.debug:
                _log.debug("No device found, using cleanup-only mode")
            return _clean_traceroute_only(output, query)

        if params is None:
            if Settings.debug:
                _log.debug("No params found, using cleanup-only mode")
            return _clean_traceroute_only(output, query)

        if not getattr(params, "structured", None):
            if Settings.debug:
                _log.debug("Structured output not configured, using cleanup-only mode")
            return _clean_traceroute_only(output, query)

        if getattr(params.structured, "enable_for_traceroute", None) is False:
            if Settings.debug:
                _log.debug("Structured output disabled for traceroute, using cleanup-only mode")
            return _clean_traceroute_only(output, query)

        if Settings.debug:
            _log.debug("Processing traceroute with structured output enabled")

        # Clean the output first using garbage cleaner before parsing
        cleaned_output = _clean_traceroute_only(output, query)
        if Settings.debug:
            _log.debug("Applied garbage cleaning before structured parsing")

        return parse_mikrotik_traceroute(cleaned_output, target, source)
