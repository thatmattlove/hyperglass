"""Tasks to be executed from web API."""

# Standard Library
import re
from typing import Dict, Union
from pathlib import Path

# Third Party
from httpx import Headers


def import_public_key(
    app_path: Union[Path, str], device_name: str, keystring: str
) -> bool:
    """Import a public key for hyperglass-agent.

    Arguments:
        app_path {Path|str} -- hyperglass app path
        device_name {str} -- Device name
        keystring {str} -- Public key

    Raises:
        RuntimeError: Raised if unable to create certs directory
        RuntimeError: Raised if written key does not match input

    Returns:
        {bool} -- True if file was written
    """
    if not isinstance(app_path, Path):
        app_path = Path(app_path)

    cert_dir = app_path / "certs"

    if not cert_dir.exists():
        cert_dir.mkdir()

    if not cert_dir.exists():
        raise RuntimeError(f"Failed to create certs directory at {str(cert_dir)}")

    filename = re.sub(r"[^A-Za-z0-9]", "_", device_name) + ".pem"
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
