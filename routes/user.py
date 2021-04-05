from api_handlers import users
from app_init import app
from util import POST_REQUEST, ParsedRequest, api_response, json_response


# user registration route
# POST request
@app.route("/accounts/register/", **POST_REQUEST)
@app.route("/register", **POST_REQUEST)
@api_response
def register():
    return users.register(ParsedRequest())


@app.route("/accounts/login", **POST_REQUEST)
@api_response
def login():
    return users.login(ParsedRequest())


@app.route("/accounts/whoami/", strict_slashes=False)
@api_response
def check_auth_resp():
    return users.check_auth()


# refresh the JWT Token
# GET request
@app.route("/accounts/token/refresh/", strict_slashes=False)
@api_response
def refesh_token():
    return users.re_authenticate(ParsedRequest())


# ===========================================================================
#                                  Users


# Get user info, secure data is removed for unauthenticated
# requests
@app.route("/accounts/<user>/", strict_slashes=False)
@api_response
def user_details(user):
    return users.get_user_details(ParsedRequest(), user)


# edit user info, only authenticated requests allowed
@app.route("/accounts/<user>/edit/", **POST_REQUEST)
@api_response
def edit_user(user):
    return users.edit(ParsedRequest(), user)


@app.route("/logout/", strict_slashes=False)
@api_response
def log_user_out():
    return json_response({}, headers={"x-access-token": "", "x-refresh-token": ""})
