from flask import request as flask_request
from psycopg2 import IntegrityError

from app_init import UserTable
from auth_token import (
    issue_access_token,
    issue_refresh_token,
    regenerate_access_token,
    require_jwt,
)
from danger import (
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    check_password_hash,
    create_token,
    decode_token,
)

from util import AppException
from util import ParsedRequest as _Parsed
from util import json_response

from .common import add_to_db, get_user_by_id, save_to_db
from .cred_manager import CredManager


def register(request: _Parsed):
    json = request.json
    get = json.get
    user = get("user")
    name = get("name")
    password = get("password")

    try:
        user_data = UserTable(user, name, password)
        add_to_db(user_data)
        return user_data.as_json
    except Exception as e:
        if isinstance(getattr(e, "orig", None), IntegrityError):
            raise AppException("User exists")
        raise e


def login(request: _Parsed):
    json = request.json
    get = json.get
    user = get("user", "").strip()
    password = get("password", "")
    invalids = []
    if not user:
        invalids.append("username")
    if not password:
        invalids.append("password")
    if invalids:
        raise AppException(f"Invalid {' and '.join(invalids)}")
    user_data = get_user_by_id(user)
    password_hash = user_data.password_hash
    if not check_password_hash(password_hash, password):
        raise AppException("Incorrect Password")
    username = user_data.user
    access_token = create_token(issue_access_token(username))
    refresh_token = create_token(issue_refresh_token(username, password_hash))

    return json_response(
        {"success": True, "user_data": user_data.as_json},
        headers={"x-access-token": access_token, "x-refresh-token": refresh_token},
    )


def re_authenticate(req: _Parsed):
    headers = flask_request.headers
    access_token = headers.get("x-access-token")
    decoded_access = decode_token(access_token)

    if decoded_access is None:
        refresh_token = headers.get("x-refresh-token")
        decoded_refresh = decode_token(refresh_token)
        access, refresh = regenerate_access_token(decoded_refresh)
        if access is None:
            raise AppException("re-auth")

        return json_response(
            {},
            headers={
                "x-access-token": create_token(access),
                "x-refresh-token": create_token(refresh),
            },
        )


# creds  will be injected by require_jwt
@require_jwt(strict=False)
def get_user_details(request: _Parsed, user: str, creds: CredManager = CredManager):
    current_user = creds.user
    if user == "me" or current_user == user.lower():
        if current_user is not None:
            return self_details(request, creds)
        raise AppException("Not Authenticated")
    user_details = get_user_by_id(user)
    json = user_details.as_json
    json.pop("_secure_")
    return {"user_data": json}


def self_details(request: _Parsed, creds: CredManager):
    req = get_user_by_id(creds.user)
    resp = req.as_json
    return {"user_data": resp}


@require_jwt()
def edit(request: _Parsed, user: str, creds: CredManager = CredManager):
    editable_fields = ("email", "school", "name")
    current_user = creds.user
    if user != current_user:
        raise AppException("Cannot edit ( not allowed )")
    json = request.json
    edit_field = json.get("field")
    if edit_field not in editable_fields:
        raise AppException("Requested field cannot be edited")
    new_value = json.get("new_value")
    user_data = get_user_by_id(current_user)

    setattr(user_data, edit_field, new_value)
    save_to_db()
    return user_data.as_json


@require_jwt()
def check_auth(creds=CredManager):
    return {"username": creds.user}
