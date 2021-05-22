from server.app_init import app
from server.util import ParsedRequest, api_response
from server.api_handlers import admin, user


# user registration route
# POST request
@router.post("/accounts/register")
@router.post("/register")
@api_response
async def register():
    return user.register(ParsedRequest())


@router.post("/accounts/login")
@api_response
async def login():
    return user.login(ParsedRequest())


# refresh the JWT Token
# GET request
@router.get("/accounts/token/refresh")
@api_response
async def refesh_token():
    return user.re_authenticate(ParsedRequest())


# ===========================================================================
#                                  Users


# Get user info, secure data is removed for unauthenticated requests
@router.get("/accounts/<user_name>")
@api_response
async def user_details(user_name):
    return user.get_user_details(user_name)


@router.patch("/accounts/<user_name>")
@api_response
async def edit_user_details(user_name):
    return user.edit(ParsedRequest(), user_name)


@router.delete("/accounts/<user_name>")
@api_response
async def delete_user_details(user_name):
    return admin.delete(user_name)


@router.post("/accounts/email-verification")
@api_response
async def send_verification_email():
    return user.send_verification_email(ParsedRequest())


@router.patch("/accounts/email-verification")
@api_response
async def confirm_email():
    return user.confirm_email(ParsedRequest())


@router.post("/accounts/<user_name>/password/new")
@api_response
async def send_password_reset_email(user_name):
    return user.send_password_reset_email(ParsedRequest(), user_name)


@router.patch("/accounts/<user_name>/password/new")
@api_response
async def verify_password_reset(user_name):
    return user.verify_password_reset(ParsedRequest(), user_name)
