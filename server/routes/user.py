from server.api_handlers import user
from server.app_init import app
from server.util import POST_REQUEST, ParsedRequest, api_response, json_response


# user registration route
# POST request
@app.route("/accounts/register/", **POST_REQUEST)
@app.route("/register", **POST_REQUEST)
@api_response
def register():
    return user.register(ParsedRequest())


@app.route("/accounts/login", **POST_REQUEST)
@api_response
def login():
    return user.login(ParsedRequest())


@app.route("/accounts/whoami/", strict_slashes=False)
@api_response
def check_auth_resp():
    return user.check_auth()


# refresh the JWT Token
# GET request
@app.route("/accounts/token/refresh/", strict_slashes=False)
@api_response
def refesh_token():
    return user.re_authenticate(ParsedRequest())


# ===========================================================================
#                                  Users


# Get user info, secure data is removed for unauthenticated
# requests
@app.route("/accounts/<user_name>/", strict_slashes=False)
@api_response
def user_details(user_name):
    return user.get_user_details(ParsedRequest(), user_name)


@app.route("/accounts/email-verification/send/", **POST_REQUEST)
@api_response
def send_verification_email():
    return user.send_verification_email(ParsedRequest())


@app.route("/accounts/email-verification/confirm/", **POST_REQUEST)
@api_response
def confirm_email():
    return user.confirm_email(ParsedRequest())


@app.route("/accounts/<user_name>/password/new/request/", **POST_REQUEST)
@api_response
def send_password_reset_email(user_name):
    return user.send_password_reset_email(ParsedRequest(), user_name)


@app.route("/accounts/<user_name>/password/new/verify/", **POST_REQUEST)
@api_response
def verify_password_reset(user_name):
    return user.verify_password_reset(ParsedRequest(), user_name)


# edit user info, only authenticated requests allowed
@app.route("/admin/accounts/<user_name>/edit/", **POST_REQUEST)
@app.route("/accounts/<user_name>/edit/", **POST_REQUEST)
@api_response
def edit_user(user_name):
    return user.edit(ParsedRequest(), user_name)


# @app.route("/logout/", strict_slashes=False)
# @api_response
# def log_user_out():
#     return json_response({}, headers={"x-access-token": "", "x-refresh-token": ""})
