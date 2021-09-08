"""Handle JSON Web Token Encoding & Decoding."""

# Standard Library
import datetime

# Third Party
import jwt


async def jwt_decode(payload: str, secret: str) -> str:
    """Decode & validate an encoded JSON Web Token (JWT)."""
    decoded = jwt.decode(payload, secret, algorithm="HS256")
    decoded = decoded["payload"]
    return decoded


async def jwt_encode(payload: str, secret: str, duration: int) -> str:
    """Encode a query to a JSON Web Token (JWT)."""
    token = {
        "payload": payload,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=duration),
    }
    encoded = jwt.encode(token, secret, algorithm="HS256").decode("utf-8")
    return encoded
