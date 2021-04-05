# ==============================================================
#                        Danger Zone
#   All the code needed to manage password
#   hashing and JWT Token creation/validation.
#   Other implementation ( Like storing the passwords
#   or requesting a new access_token to be done elsewhere )
# ==============================================================

from time import time as _time

import jwt as _jwt
import passlib.hash as _pwhash
from constants import (
    SIGNING_KEY as _SIGNING_KEY,
    TOKEN_EXPIRATION_TIME_IN_SECONDS as _TOKEN_EXPIRATION_TIME_IN_SECONDS,
)
from util import AppException

if _SIGNING_KEY is None:
    raise Exception(
        "No JWT Signing key found in this environment! Authentication will not work"
    )
if _TOKEN_EXPIRATION_TIME_IN_SECONDS is None:
    raise Exception("Specify token expiration time..")

_hash_method = _pwhash.scrypt  # or argon2? needs external dependency

_encode_token = _jwt.encode
_decode_token = _jwt.decode

# =======================================================================
#                       Password Hashing
def check_password_hash(_hash: str, pw: str) -> bool:
    return _hash_method.verify(pw, _hash)


def generate_password_hash(pw):
    return _hash_method.hash(pw)


# =======================================================================

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"

_ALLOWED_TOKEN_TYPES = (ACCESS_TOKEN, REFRESH_TOKEN)

_EXPIRED = _jwt.exceptions.ExpiredSignatureError

# =======================================================================
#                            JWT Token Management
def create_token(data: dict) -> str:
    token_type = data.get("token_type")
    if token_type is None or token_type not in _ALLOWED_TOKEN_TYPES:
        raise Exception("Invalid token type")
    if token_type == ACCESS_TOKEN:
        # data['exp'] is JWT Spec for defining expireable tokens
        data["exp"] = _time() + _TOKEN_EXPIRATION_TIME_IN_SECONDS
    return to_str(_encode_token(data, _SIGNING_KEY, algorithm="HS512"))


def decode_token(data: str) -> dict:
    try:
        return _decode_token(data, _SIGNING_KEY, algorithms=["HS512"])
    except _EXPIRED:
        return None
    except Exception as e:
        print(e)
        raise AppException("Invalid token", 400)


def to_str(x):
    return x.decode() if isinstance(x, bytes) else x


# =======================================================================
