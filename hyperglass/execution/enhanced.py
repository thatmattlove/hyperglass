"""Example integration of BGP.tools enrichment into the main execution flow."""

# Standard Library
import typing as t

# Project
from hyperglass.log import log
from hyperglass.execution.main import execute as original_execute
from hyperglass.execution.enrichment import execute_with_enrichment
from hyperglass.models.data import OutputDataModel

if t.TYPE_CHECKING:
    from hyperglass.models.api import Query


async def execute_enhanced(query: "Query") -> t.Union[OutputDataModel, str]:
    """Enhanced execute function with BGP.tools enrichment.

    This can be used to replace the original execute function in hyperglass.execution.main
    to add automatic BGP.tools enrichment to all query results.

    Usage:
        # In hyperglass/api/routes.py, replace:
        # from hyperglass.execution.main import execute
        # with:
        # from hyperglass.execution.enhanced import execute_enhanced as execute
    """
    return await execute_with_enrichment(query, original_execute)


# Optional: Patch the original execute function
def monkey_patch_execute():
    """Monkey patch the original execute function with enhanced version.

    This can be called during application startup to automatically enable
    BGP.tools enrichment without changing imports throughout the codebase.

    Usage:
        # In hyperglass application startup code:
        from hyperglass.execution.enhanced import monkey_patch_execute
        monkey_patch_execute()
    """
    import hyperglass.execution.main
    import hyperglass.api.routes

    # Replace the execute function in both modules
    hyperglass.execution.main.execute = execute_enhanced
    hyperglass.api.routes.execute = execute_enhanced

    log.info("BGP.tools enrichment enabled via monkey patching")
