"""Decorators that ensure authentication is provided
"""

from http import HTTPStatus
from time import time
from flask import request
from .danger import (
    EMAIL_CONF_TOKEN,
    RESET_PASSWORD_TOKEN,
    decode_token as decode,
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    check_password_hash as check,
    generate_password_hash,
)
from .api_handlers.common import get_user_by_id
from .util import AppException, get_bearer_token
from .api_handlers.cred_manager import CredManager
from .constants import REFRESH_TOKEN_SALT

THREE_HOURS = 3 * 60 * 60


def require_jwt(strict=True, admin_mode=False):
    # use this wherever you need the user to provide authentication data
    # pass strict=True if you absolutely need an authenticated user to access the route
    def wrapper(func):
        def run(*args, **kwargs):
            access = get_token(strict=strict)
            cred = CredManager(access)
            kwargs["creds"] = cred
            if admin_mode and not cred.is_admin:
                raise AppException("No.", HTTPStatus.FORBIDDEN)
            return func(*args, **kwargs)

        return run

    return wrapper


def regenerate_access_token(refresh: dict) -> dict:
    user = refresh.get("user")
    integrity = refresh.get("integrity")
    data = get_user_by_id(user)
    is_admin = data.is_admin
    current = get_integrity(data.user, data.password_hash)
    if check(integrity, current):
        return (
            issue_access_token(user, is_admin),
            issue_refresh_token(user, data.password_hash),
        )
    return None, None


def issue_access_token(username: str, is_admin: bool):
    return {"token_type": ACCESS_TOKEN, "user": username, "is_admin": is_admin}


def issue_email_confirmation_token(user: str):
    return {"token_type": EMAIL_CONF_TOKEN, "user": user, "exp": time() + THREE_HOURS}


def issue_password_reset_token(user: str):
    return {
        "token_type": RESET_PASSWORD_TOKEN,
        "user": user,
        "exp": time() + THREE_HOURS,
    }


def issue_refresh_token(username, password_hash):
    return {
        "token_type": REFRESH_TOKEN,
        "user": username,
        "integrity": generate_password_hash(get_integrity(username, password_hash)),
    }


def get_integrity(username: str, password_hash: str):
    # in case you need to invalidate EVERY users tokens,
    # change the refresh token salt
    return f"{username}{REFRESH_TOKEN_SALT}{password_hash}"


def get_token(strict=True):
    headers = request.headers
    received_access_token = get_bearer_token(headers)

    if not received_access_token:
        if strict:
            raise AppException(
                "No authentication provided", HTTPStatus.UNPROCESSABLE_ENTITY
            )
        return None
    try:
        access = decode(received_access_token)
    except Exception:
        if strict:
            raise AppException("invalid token", HTTPStatus.BAD_REQUEST)
        return None

    if access is None:
            raise AppException("refresh", HTTPStatus.OK)

    return access
