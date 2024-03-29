"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
import signal
from typing import Any, Dict, Union, Callable, Sequence

# Project
from hyperglass.log import log
from hyperglass.exceptions import DeviceTimeout, ResponseEmpty
from hyperglass.models.api import Query
from hyperglass.configuration import params

# Local
from .drivers import Connection, AgentConnection, NetmikoConnection, ScrapliConnection


def map_driver(driver_name: str) -> Connection:
    """Get the correct driver class based on the driver name."""

    if driver_name == "scrapli":
        return ScrapliConnection

    elif driver_name == "hyperglass_agent":
        return AgentConnection

    return NetmikoConnection


def handle_timeout(**exc_args: Any) -> Callable:
    """Return a function signal can use to raise a timeout exception."""

    def handler(*args: Any, **kwargs: Any) -> None:
        raise DeviceTimeout(**exc_args)

    return handler


async def execute(query: Query) -> Union[str, Sequence[Dict]]:
    """Initiate query validation and execution."""

    output = params.messages.general

    log.debug("Received query for {}", query.json())
    log.debug("Matched device config: {}", query.device)

    mapped_driver = map_driver(query.device.driver)
    driver = mapped_driver(query.device, query)

    timeout_args = {
        "unformatted_msg": params.messages.connection_error,
        "device_name": query.device.name,
        "error": params.messages.request_timeout,
    }

    if query.device.proxy:
        timeout_args["proxy"] = query.device.proxy.name

    signal.signal(signal.SIGALRM, handle_timeout(**timeout_args))
    signal.alarm(params.request_timeout - 1)

    if query.device.proxy:
        proxy = driver.setup_proxy()
        with proxy() as tunnel:
            response = await driver.collect(
                tunnel.local_bind_host, tunnel.local_bind_port
            )
    else:
        response = await driver.collect()

    output = await driver.parsed_response(response)

    if isinstance(output, str):
        # If the output is a string (not structured) and is empty,
        # produce an error.
        if output == "" or output == "\n":
            raise ResponseEmpty(
                params.messages.no_output, device_name=query.device.name
            )
    elif isinstance(output, Dict):
        # If the output an empty dict, responses have data, produce an
        # error.
        if not output:
            raise ResponseEmpty(
                params.messages.no_output, device_name=query.device.name
            )

    log.debug("Output for query: {}:\n{}", query.json(), repr(output))
    signal.alarm(0)

    return output
