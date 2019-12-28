# Standard Library Imports
import datetime

# Third Party Imports
import jwt

# Project Imports
from hyperglass.exceptions import RestError


async def jwt_decode(payload, secret):
    """Decode & validate an encoded JSON Web Token (JWT)"""
    try:
        decoded = jwt.decode(payload, secret, algorithm="HS256")
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise RestError(str(exp)) from None


async def jwt_encode(payload, secret, duration):
    """Encode a query to a JSON Web Token (JWT)"""
    token = {
        "payload": payload,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=duration),
    }
    encoded = jwt.encode(token, secret, algorithm="HS256").decode("utf-8")
    return encoded
