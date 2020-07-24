"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
import signal
from typing import Any, Dict, Union, Callable

# Project
from hyperglass.log import log
from hyperglass.util import validate_nos
from hyperglass.exceptions import DeviceTimeout, ResponseEmpty
from hyperglass.configuration import params, devices
from hyperglass.api.models.query import Query
from hyperglass.execution.drivers import (
    AgentConnection,
    NetmikoConnection,
    ScrapliConnection,
)

DRIVER_MAP = {
    "scrapli": ScrapliConnection,
    "netmiko": NetmikoConnection,
    "hyperglass_agent": AgentConnection,
}


def handle_timeout(**exc_args: Any) -> Callable:
    """Return a function signal can use to raise a timeout exception."""

    def handler(*args: Any, **kwargs: Any) -> None:
        raise DeviceTimeout(**exc_args)

    return handler


async def execute(query: Query) -> Union[str, Dict]:
    """Initiate query validation and execution."""

    output = params.messages.general
    device = getattr(devices, query.query_location)

    log.debug(f"Received query for {query}")
    log.debug(f"Matched device config: {device}")

    supported, driver_name = validate_nos(device.nos)

    mapped_driver = DRIVER_MAP.get(driver_name, NetmikoConnection)
    driver = mapped_driver(device, query)

    timeout_args = {
        "unformatted_msg": params.messages.connection_error,
        "device_name": device.display_name,
        "error": params.messages.request_timeout,
    }

    if device.proxy:
        timeout_args["proxy"] = device.proxy.name

    signal.signal(signal.SIGALRM, handle_timeout(**timeout_args))
    signal.alarm(params.request_timeout - 1)

    if device.proxy:
        proxy = driver.setup_proxy()
        with proxy() as tunnel:
            response = await driver.collect(
                tunnel.local_bind_host, tunnel.local_bind_port
            )
    else:
        response = await driver.collect()

    output = await driver.parsed_response(response)

    if output == "" or output == "\n":
        raise ResponseEmpty(params.messages.no_output, device_name=device.display_name)

    log.debug(f"Output for query: {query.json()}:\n{repr(output)}")
    signal.alarm(0)

    return output
