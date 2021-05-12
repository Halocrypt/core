from server.app_init import app
from server.util import ParsedRequest, api_response
from server.api_handlers import admin, user


# user registration route
# POST request
@app.post("/accounts/register/", strict_slashes=False)
@app.post("/register", strict_slashes=False)
@api_response
def register():
    return user.register(ParsedRequest())


@app.post("/accounts/login", strict_slashes=False)
@api_response
def login():
    return user.login(ParsedRequest())


# refresh the JWT Token
# GET request
@app.get("/accounts/token/refresh/", strict_slashes=False)
@api_response
def refesh_token():
    return user.re_authenticate(ParsedRequest())


# ===========================================================================
#                                  Users


# Get user info, secure data is removed for unauthenticated requests
@app.get("/accounts/<user_name>/", strict_slashes=False)
@api_response
def user_details(user_name):
    return user.get_user_details(user_name)


@app.patch("/accounts/<user_name>/", strict_slashes=False)
@api_response
def edit_user_details(user_name):
    return user.edit(ParsedRequest(), user_name)


@app.delete("/accounts/<user_name>/", strict_slashes=False)
@api_response
def delete_user_details(user_name):
    return admin.delete(user_name)


@app.post("/accounts/email-verification/", strict_slashes=False)
@api_response
def send_verification_email():
    return user.send_verification_email(ParsedRequest())


@app.patch("/accounts/email-verification/", strict_slashes=False)
@api_response
def confirm_email():
    return user.confirm_email(ParsedRequest())


@app.post("/accounts/<user_name>/password/new/", strict_slashes=False)
@api_response
def send_password_reset_email(user_name):
    return user.send_password_reset_email(ParsedRequest(), user_name)


@app.patch("/accounts/<user_name>/password/new/", strict_slashes=False)
@api_response
def verify_password_reset(user_name):
    return user.verify_password_reset(ParsedRequest(), user_name)
