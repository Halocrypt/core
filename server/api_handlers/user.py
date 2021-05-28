from http import HTTPStatus
from re import IGNORECASE
from re import compile as _compile
from server.response_caching import invalidate
from urllib.parse import urlencode

# pylint: disable=no-name-in-module
from psycopg2.errors import UniqueViolation
from server.api_handlers.email import send_email
from server.api_handlers.templates import EMAIL_TEMPLATE
from server.auth_token import (
    issue_access_token,
    issue_email_confirmation_token,
    issue_password_reset_token,
    issue_refresh_token,
    regenerate_access_token,
    require_jwt,
)
from server.constants import EVENT_NAMES
from server.danger import (
    EMAIL_CONF_TOKEN,
    RESET_PASSWORD_TOKEN,
    check_password_hash,
    create_token,
    decode_token,
)
from server.models import User
from server.util import AppException
from server.util import ParsedRequest
from server.util import ParsedRequest as _Parsed
from server.util import get_bearer_token, json_response

from .common import (
    add_to_db,
    clean_secure,
    get_user_by_id,
    save_to_db,
    send_acount_creation_webhook,
    send_admin_action_webhook,
)
from .cred_manager import CredManager

# regex to find the offending column
# there must be a better way - RH
find_error = _compile(
    r"Key\s*\(\"?(?P<key>.*?)\"?\)=\((?P<val>.*?)\)", IGNORECASE
).search


def get_integrity_error_cause(error_message: str):
    try:
        match = find_error(error_message)
        print(error_message)
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
    email = get("email")
    institution = get("institution")
    password = get("password")
    event = get("event")
    if event == "intra":
        raise AppException("Inta is over..see you in the main event")
    try:
        user_data = User(
            user=user,
            name=name,
            email=email,
            institution=institution,
            password=password,
            event=event,
        )
        js = user_data.as_json
        add_to_db(user_data)
        send_acount_creation_webhook(user, name, event)
        return invalidate(f"{event}-leaderboard", js)
    except Exception as e:
        check_integrity_error(e)


def login(request: _Parsed):
    json = request.json
    get = json.get
    user = get("user", "").strip().lower()
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


@require_jwt()
def send_verification_email(req: ParsedRequest, creds: CredManager = CredManager):
    handler = get_subdomain(req.json.get("handler"))
    user = creds.user
    user_data = get_user_by_id(user)
    token = create_token(issue_email_confirmation_token(user))
    qs = urlencode({"token": token, "user": user})
    url = f"https://{handler}.halocrypt.com/-/confirm-email?{qs}"
    send_email(
        user_data.email,
        "Confirm Email",
        EMAIL_TEMPLATE.replace(r"{url}", url)
        .replace(r"{message}", "Click the button below to verify your email")
        .replace(r"{action}", "Verify Email"),
        f"Confirm your email here {url}",
    )
    return {"success": True}


def confirm_email(req: _Parsed):
    token = req.json.get("token")
    data = decode_token(token)
    if data is None:
        raise AppException("Token expired", HTTPStatus.UNAUTHORIZED)
    if data["token_type"] == EMAIL_CONF_TOKEN:
        user = data["user"]
        u = get_user_by_id(user)
        if u.has_verified_email:
            return {"success": True}
        u.has_verified_email = True
        save_to_db()
        return {"success": True}

    raise AppException("Invalid token", HTTPStatus.BAD_REQUEST)


def send_password_reset_email(req: _Parsed, user):
    handler = get_subdomain(req.json.get("handler"))

    user_data = get_user_by_id(user)
    token = create_token(
        issue_password_reset_token(user_data.user, user_data.password_hash)
    )
    qs = urlencode({"token": token, "user": user})
    url = f"https://{handler}.halocrypt.com/-/reset-password?{qs}"

    if not user:
        raise AppException("Invalid request")
    send_email(
        user_data.email,
        "Reset password",
        EMAIL_TEMPLATE.replace(r"{url}", url)
        .replace(
            r"{message}",
            "Our records indicate that you have requested a password reset. You can do so by clicking the button below",
        )
        .replace(r"{action}", "Reset Password"),
        f"Reset your password here: {url}",
    )
    return {"success": True}


def get_subdomain(handler):
    if handler not in EVENT_NAMES:
        raise AppException("Invalid handler")
    return "www" if handler == "main" else handler


def verify_password_reset(req: _Parsed, user_name: str):
    token = req.json.get("token")
    new_password = req.json.get("new_password")
    data = decode_token(token)

    if data is None:
        raise AppException("Token expired", HTTPStatus.UNAUTHORIZED)
    if data["token_type"] == RESET_PASSWORD_TOKEN:
        user = data["user"]
        if user != user_name.lower():
            raise AppException("Lol")
        u = get_user_by_id(user)
        state = data["state"]
        if not check_password_hash(state, f"{u.user}{u.password_hash}"):
            raise AppException("Token expired", HTTPStatus.UNAUTHORIZED)
        u.password_hash = new_password
        save_to_db()
        return {"success": True}

    raise AppException("Invalid token", HTTPStatus.BAD_REQUEST)


def re_authenticate(req: _Parsed):
    headers = req.headers
    access_token = get_bearer_token(req.headers)
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
def get_user_details(user: str, creds: CredManager = CredManager):
    current_user = creds.user
    if user == "me" or current_user == user.lower():
        if current_user is not None:
            return self_details(creds)
        raise AppException("Not Authenticated", HTTPStatus.UNAUTHORIZED)

    user_details = get_user_by_id(user)
    if not creds.is_admin:
        json = clean_secure(user_details)
    else:
        json = user_details.as_json
    return {"user_data": json}


def self_details(creds: CredManager):
    req = get_user_by_id(creds.user)
    resp = req.as_json
    return {"user_data": resp}


editable_fields = ("email", "institution", "name")


@require_jwt()
def edit(request: _Parsed, user: str, creds: CredManager = CredManager):
    current_user = creds.user
    if user != current_user and not creds.is_admin:
        raise AppException("Cannot edit ( not allowed )", HTTPStatus.FORBIDDEN)

    json = request.json
    keys = json.keys()

    if any(x not in editable_fields for x in keys) and not creds.is_admin:
        raise AppException("Requested field cannot be edited", HTTPStatus.BAD_REQUEST)

    user_data = get_user_by_id(user)
    text = []
    who = creds.user
    did_change = False
    for k, v in json.items():
        prev = getattr(user_data, k, "N/A")
        if prev == v:
            continue
        did_change = True
        setattr(user_data, k, v)
        if creds.is_admin:
            text.append(f"{who} changed {k} of `{user}` from `{prev}` to `{v}`")

        if k == "email":
            user_data.has_verified_email = False
    event = user_data.event
    js = user_data.as_json
    try:
        save_to_db()
    except Exception as e:
        check_integrity_error(e)

    if creds.is_admin and text:
        send_admin_action_webhook(text)
    if did_change:
        return invalidate(f"{event}-leaderboard", js)
    return js


@require_jwt()
def check_auth(creds=CredManager):
    return {"username": creds.user}


def check_integrity_error(e):
    # pylint: disable=E1101
    orig = getattr(e, "orig", None)
    if isinstance(orig, UniqueViolation):
        args = orig.args[0]
        ret = get_integrity_error_cause(args)
        if ret is None:
            raise AppException("User exists", HTTPStatus.BAD_REQUEST)
        k, v = ret
        raise AppException(f'Another account exists with the {k} "{v}"')
    raise e
    # pylint: enable=E1101
