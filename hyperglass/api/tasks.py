"""Tasks to be executed from web API."""

# Standard Library
from typing import Dict, Union
from pathlib import Path
from datetime import datetime

# Third Party
from httpx import Headers
from starlette.requests import Request

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.external import Webhook, bgptools
from hyperglass.models.api import Query

__all__ = (
    "import_public_key",
    "process_headers",
    "send_webhook",
)


def import_public_key(app_path: Union[Path, str], device_name: str, keystring: str) -> bool:
    """Import a public key for hyperglass-agent."""
    if not isinstance(app_path, Path):
        app_path = Path(app_path)

    cert_dir = app_path / "certs"

    if not cert_dir.exists():
        cert_dir.mkdir()

    if not cert_dir.exists():
        raise RuntimeError(f"Failed to create certs directory at {str(cert_dir)}")

    filename = f"{device_name}.pem"
    cert_file = cert_dir / filename

    with cert_file.open("w+") as file:
        file.write(str(keystring))

    with cert_file.open("r") as file:
        read_file = file.read().strip()
        if not keystring == read_file:
            raise RuntimeError("Wrote key, but written file did not match input key")

    return True


async def process_headers(headers: Headers) -> Dict:
    """Filter out unwanted headers and return as a dictionary."""
    headers = dict(headers)
    header_keys = (
        "user-agent",
        "referer",
        "accept-encoding",
        "accept-language",
        "x-real-ip",
        "x-forwarded-for",
    )
    return {k: headers.get(k) for k in header_keys}


async def send_webhook(
    query_data: Query,
    request: Request,
    timestamp: datetime,
):
    """If webhooks are enabled, get request info and send a webhook."""
    params = use_state("params")
    try:
        if params.logging.http is not None:
            headers = await process_headers(headers=request.headers)

            if headers.get("x-real-ip") is not None:
                host = headers["x-real-ip"]
            elif headers.get("x-forwarded-for") is not None:
                host = headers["x-forwarded-for"]
            else:
                host = request.client.host

            network_info = await bgptools.network_info(host)

            async with Webhook(params.logging.http) as hook:

                await hook.send(
                    query={
                        **query_data.dict(),
                        "headers": headers,
                        "source": host,
                        "network": network_info.get(host, {}),
                        "timestamp": timestamp,
                    }
                )
    except Exception as err:
        log.error("Error sending webhook to {}: {}", params.logging.http.provider, str(err))
