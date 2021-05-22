from typing import Optional
from urllib.parse import urlencode

from app.db.models.user import User
from app.db.mutations import add_to_db, delete_from_db
from app.db.queries import get_user_by_id
from app.dependencies import inject_db, require_auth
from app.internal import email
from app.internal.api_response import api_response
from app.internal.auth_token import (
    authenticate,
    issue_email_confirmation_token,
    issue_password_reset_token,
    regenerate_access_token,
)
from app.internal.constants import EDITABLE_FIELDS
from app.internal.danger import (
    EMAIL_CONF_TOKEN,
    RESET_PASSWORD_TOKEN,
    check_password_hash,
    create_token,
    decode_token,
)
from app.internal.response_caching import invalidate
from app.internal.router import Router
from app.internal.util import check_integrity_error
from app.internal.webhooks import (
    send_acount_creation_webhook,
    send_admin_action_webhook,
    send_email_verify_webhook,
    send_password_reset_webhook,
)
from app.models.ext import (
    APIResponse,
    EmailRequest,
    NewPassword,
    UserSession,
    VerifyToken,
)
from app.models.user import UserCreds, UserDetails, UserRegister, UserResponseSecure
from fastapi import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.params import Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

router = Router(tags=["user"])


@router.post("/accounts/register", response_model=APIResponse[UserResponseSecure])
@router.post(
    "/register", response_model=APIResponse[UserResponseSecure], include_in_schema=False
)
@api_response
async def register(
    json: UserRegister,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(inject_db),
):
    event = json.event
    user_data = User(**json.dict())
    if event == "intra":
        raise HTTPException(400, "Intra is over")
    js = user_data.as_json
    try:
        await add_to_db(db, user_data)
    except Exception as e:
        check_integrity_error(e)
    background_task.add_task(send_acount_creation_webhook, json.user, json.name, event)
    return invalidate(f"{event}-leaderboard", js)


@router.post("/oauth/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(inject_db),
):
    access, _, __ = await authenticate(db, form_data.username, form_data.password)
    return {"access_token": access, "token_type": "bearer"}


@router.post("/accounts/login", response_model=APIResponse[UserResponseSecure])
@api_response
async def login(
    json: UserCreds,
    db: AsyncSession = Depends(inject_db),
):
    access, refresh, user_data = await authenticate(db, json.user, json.password)
    return JSONResponse(
        {"success": True, "user_data": user_data.as_json},
        headers={"x-access-token": access, "x-refresh-token": refresh},
    )


@router.get("/accounts/token/refresh")
@api_response
async def refesh_token(
    authorization: Optional[str] = Header(None),
    x_refresh_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(inject_db),
):

    decoded_access = decode_token(
        (authorization or "").replace("Bearer ", "", 1).strip()
    )
    if decoded_access is None:
        decoded_refresh = decode_token(x_refresh_token)
        access, refresh = await regenerate_access_token(db, decoded_refresh)
        if access is None:
            raise HTTPException(403, "re-auth")
        return JSONResponse(
            {},
            headers={
                "x-access-token": create_token(access),
                "x-refresh-token": create_token(refresh),
            },
        )


# ===========================================================================
#                                  Users


@router.post("/accounts/email-verification")
@api_response
async def send_verification_email(
    json: EmailRequest,
    auth: UserSession = Depends(require_auth),
    db: AsyncSession = Depends(inject_db),
):
    subdomain = json.get_subdomain()
    user = auth.user
    user_data = await get_user_by_id(db, user)
    if user_data.has_verified_email:
        raise HTTPException(400, "Email already verified")
    token = create_token(issue_email_confirmation_token(user, user_data.email))
    qs = urlencode({"token": token, "user": user})
    url = f"https://{subdomain}.halocrypt.com/-/confirm-email?{qs}"
    email.send_confirmation_email(user_data.email, url)
    return {"success": True}


@router.patch("/accounts/email-verification")
@api_response
async def confirm_email(
    json: VerifyToken,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(inject_db),
):
    token = json.token
    data = decode_token(token)
    if data is None:
        raise HTTPException(403, "Token expired.")
    if data["token_type"] == EMAIL_CONF_TOKEN:
        user = data["user"]
        user_data = await get_user_by_id(db, user)
        if data["email"] != user_data.email:
            raise HTTPException(422, "Token expired")
        if user_data.has_verified_email:
            return {"success": True}
        user_data.has_verified_email = True
        await db.commit()
        background_task.add_task(send_email_verify_webhook, user)
        return {"success": True}
    raise HTTPException(400, "Invalid token")


@router.post("/accounts/{user}/password/new")
@api_response
async def send_password_reset_email(
    user: str,
    json: EmailRequest,
    db: AsyncSession = Depends(inject_db),
):
    subdomain = json.get_subdomain()
    user_data = await get_user_by_id(db, user)
    token = create_token(issue_password_reset_token(user, user_data.password_hash))
    qs = urlencode({"token": token, "user": user})
    url = f"https://{subdomain}.halocrypt.com/-/reset-password?{qs}"
    email.send_password_reset_email(user_data.email, url)
    return {"success": True}


@router.patch("/accounts/{user}/password/new")
@api_response
async def verify_password_reset(
    user: str,
    json: NewPassword,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(inject_db),
):
    token = json.token
    password = json.new_password
    data = decode_token(token)
    if data is None:
        raise HTTPException(403, "Token Expired.")
    if data["token_type"] == RESET_PASSWORD_TOKEN:
        target = data["user"]
        if target != user:
            raise HTTPException(403, "Lol")
        state = data["state"]
        user_data = await get_user_by_id(db, target)
        if not check_password_hash(state, f"{user_data.user}{user_data.password_hash}"):
            raise HTTPException(403, "Token Expired")
        user_data.password_hash = password
        await db.commit()
        background_task.add_task(send_password_reset_webhook, user)
        return {"success": True}
    else:
        raise HTTPException(400, "Invalid token")


# Get user info, secure data is removed for unauthenticated requests
@router.get(
    "/accounts/{user}",
    response_model=APIResponse[UserDetails],
)
@api_response
async def user_details(
    user: str,
    auth: UserSession = Depends(require_auth.lax),
    db: AsyncSession = Depends(inject_db),
):
    if user == "me":
        if not auth.user:
            raise HTTPException(401, "Not authenticated")
        else:
            user = auth.user
    user_data = await get_user_by_id(db, user)
    show_secure = user_data.user == auth.user or auth.is_admin
    js = user_data.as_json
    if not show_secure:
        js.pop("_secure_")
    return {"user_data": js}


@router.patch("/accounts/{user}", response_model=APIResponse[UserResponseSecure])
@api_response
async def edit_user_details(
    user: str,
    json: dict,
    background_task: BackgroundTasks,
    auth: UserSession = Depends(require_auth),
    db: AsyncSession = Depends(inject_db),
):
    current = auth.user
    is_admin = auth.is_admin
    if user != current and not is_admin:
        raise HTTPException(403, "Not authorized to edit")
    keys = json.keys()
    if any(x not in EDITABLE_FIELDS for x in keys) and not is_admin:
        raise HTTPException(400, "Requested field cannot be edited")
    user_data = await get_user_by_id(db, user)
    text = []
    did_change = False

    for k, v in json.items():
        prev = getattr(user_data, k, "N/A")
        if prev == v:
            continue
        did_change = True
        setattr(user_data, k, v)
        if is_admin:
            text.append(f"{current} changed {k} of `{user}` from `{prev}` to `{v}`")
        if k == "email":
            user_data.has_verified_email = False
    event = user_data.event

    js = user_data.as_json
    if did_change:
        try:
            await db.commit()
        except Exception as e:
            check_integrity_error(e)
        if text:
            background_task.add_task(send_admin_action_webhook, text)
        return invalidate(f"{event}-leaderboard", js)
    return js


@router.delete("/accounts/{user}")
@api_response
async def delete_user_details(
    user: str,
    background_task: BackgroundTasks,
    auth: UserSession = Depends(require_auth.admin),
    db: AsyncSession = Depends(inject_db),
):
    user_data = await get_user_by_id(db, user)
    if user_data.is_admin:
        raise HTTPException(403, "Cannot delete an admin!")
    background_task.add_task(
        send_admin_action_webhook, [f"{user} was deleted by {auth.user}"]
    )
    event = user_data.event
    await delete_from_db(db, user_data)
    return invalidate(f"{event}-leaderboard", {"success": True})
