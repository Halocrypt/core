from http import HTTPStatus
from re import IGNORECASE
from re import compile as _compile

from psycopg2 import IntegrityError
from server.models import UserTable
from server.auth_token import (
    issue_access_token,
    issue_refresh_token,
    regenerate_access_token,
    require_jwt,
)
from server.danger import check_password_hash, create_token, decode_token
from server.util import AppException
from server.util import ParsedRequest as _Parsed
from server.util import json_response

from .common import add_to_db, get_user_by_id, save_to_db
from .cred_manager import CredManager

# regex to find the offending column, surprisingly
# there must be a better way - RH
find_error = _compile(r"Key\s*\(\"(?P<key>.*)?\"\)=\((?P<val>.*?)\)", IGNORECASE).search


def get_integrity_error_cause(error_message: str):
    try:
        match = find_error(error_message)
        if not match:
            return None
        k = match.group("key")
        v = match.group("val")
        return k, v
    except Exception as e:
        print(e)
        return None


def register(request: _Parsed):
    json = request.json
    get = json.get
    user = get("user")
    name = get("name")
    password = get("password")

    try:
        user_data = UserTable(user, name, password)
        js = user_data.as_json
        add_to_db(user_data)
        return js
    except Exception as e:
        # pylint: disable=E1101
        orig = getattr(e, "orig", None)
        if isinstance(orig, IntegrityError):
            args = orig.args
            ret = get_integrity_error_cause(args)
            if ret is None:
                raise AppException("User exists", HTTPStatus.BAD_REQUEST)
            k, v = ret
            raise AppException(f'Another account exists with the {k} "{v}"')
        raise e
        # pylint: enable=E1101


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
        raise AppException(
            f"Invalid {' and '.join(invalids)}", HTTPStatus.UNPROCESSABLE_ENTITY
        )
    user_data = get_user_by_id(user)
    password_hash = user_data.password_hash
    if not check_password_hash(password_hash, password):
        raise AppException("Incorrect Password", HTTPStatus.FORBIDDEN)
    username = user_data.user
    is_admin = user_data.is_admin
    access_token = create_token(issue_access_token(username, is_admin))
    refresh_token = create_token(issue_refresh_token(username, password_hash))

    return json_response(
        {"success": True, "user_data": user_data.as_json},
        headers={"x-access-token": access_token, "x-refresh-token": refresh_token},
    )


def re_authenticate(req: _Parsed):
    headers = req.headers
    access_token = headers.get("x-access-token")
    decoded_access = decode_token(access_token)

    if decoded_access is None:
        refresh_token = headers.get("x-refresh-token")
        decoded_refresh = decode_token(refresh_token)
        access, refresh = regenerate_access_token(decoded_refresh)
        if access is None:
            raise AppException("re-auth", HTTPStatus.FORBIDDEN)

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
            return self_details(creds)
        raise AppException("Not Authenticated", HTTPStatus.UNAUTHORIZED)

    user_details = get_user_by_id(user)
    json = user_details.as_json
    if not creds.is_admin:
        json.pop("_secure_")
    return {"user_data": json}


def self_details(creds: CredManager):
    req = get_user_by_id(creds.user)
    resp = req.as_json
    return {"user_data": resp}


@require_jwt()
def edit(request: _Parsed, user: str, creds: CredManager = CredManager):
    current_user = creds.user
    if user != current_user and not creds.is_admin:
        raise AppException("Cannot edit ( not allowed )", HTTPStatus.FORBIDDEN)
    editable_fields = ("email", "institution", "name")

    json = request.json
    edit_field = json.get("field")
    if not creds.is_admin and edit_field not in editable_fields:
        raise AppException("Requested field cannot be edited", HTTPStatus.BAD_REQUEST)
    new_value = json.get("new_value")
    user_data = get_user_by_id(current_user)

    setattr(user_data, edit_field, new_value)
    save_to_db()
    return user_data.as_json


@require_jwt()
def check_auth(creds=CredManager):
    return {"username": creds.user}
