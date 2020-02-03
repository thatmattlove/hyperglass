"""Handle JSON Web Token Encoding & Decoding."""

# Standard Library
import datetime

# Third Party
import jwt

# Project
from hyperglass.exceptions import RestError


async def jwt_decode(payload, secret):
    """Decode & validate an encoded JSON Web Token (JWT).

    Arguments:
        payload {str} -- Raw JWT payload
        secret {str} -- JWT secret

    Raises:
        RestError: Raised if decoded payload is improperly formatted
        or if the JWT is not able to be decoded.

    Returns:
        {str} -- Decoded response payload
    """
    try:
        decoded = jwt.decode(payload, secret, algorithm="HS256")
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise RestError(str(exp)) from None


async def jwt_encode(payload, secret, duration):
    """Encode a query to a JSON Web Token (JWT).

    Arguments:
        payload {str} -- Stringified JSON request
        secret {str} -- JWT secret
        duration {int} -- Number of seconds claim is valid

    Returns:
        str -- Encoded request payload
    """
    token = {
        "payload": payload,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=duration),
    }
    encoded = jwt.encode(token, secret, algorithm="HS256").decode("utf-8")
    return encoded
