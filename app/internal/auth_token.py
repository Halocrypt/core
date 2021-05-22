"""
Helpers that ensure authentication is provided
"""


from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.db.queries import get_user_by_id
from time import time

from .danger import (
    EMAIL_CONF_TOKEN,
    RESET_PASSWORD_TOKEN,
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    check_password_hash as check,
    create_token,
    generate_password_hash,
)


from .constants import REFRESH_TOKEN_SALT

THREE_HOURS = 3 * 60 * 60


async def regenerate_access_token(db: AsyncSession, refresh: dict) -> dict:
    user = refresh.get("user")
    integrity = refresh.get("integrity")
    data = await get_user_by_id(db, user)
    is_admin = data.is_admin
    current = get_integrity(data.user, data.password_hash)
    if check(integrity, current):
        return (
            issue_access_token(user, is_admin),
            issue_refresh_token(user, data.password_hash),
        )
    return None, None


async def authenticate(db: AsyncSession, user: str, password: str):
    user_data = await get_user_by_id(db, user)
    pw_hash = user_data.password_hash
    if not check(pw_hash, password):
        raise HTTPException(403, "Incorrect Password")
    username = user_data.user
    is_admin = user_data.is_admin
    access_token = create_token(issue_access_token(username, is_admin))
    refresh_token = create_token(issue_refresh_token(username, pw_hash))
    return access_token, refresh_token, user_data


def issue_access_token(username: str, is_admin: bool):
    return {"token_type": ACCESS_TOKEN, "user": username, "is_admin": is_admin}


def issue_email_confirmation_token(user: str, email: str):
    return {
        "token_type": EMAIL_CONF_TOKEN,
        "user": user,
        "email": email,
        "exp": time() + THREE_HOURS,
    }


def issue_password_reset_token(user, phash):
    return {
        "token_type": RESET_PASSWORD_TOKEN,
        "user": user,
        "state": generate_password_hash(f"{user}{phash}"),
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
