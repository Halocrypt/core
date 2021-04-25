from server.app_init import app
from server.util import api_response, crud

from server.resolvers import user

register_resolver = user.RegisterResolver()
login_resolver = user.LoginResolver()
authentication_resolver = user.AuthenticationResolver()
user_resolver = user.UserResolver()
email_verification_resolver = user.EmailVerificationResolver()
paassword_reset_resolver = user.PasswordResetResolver()
# user registration route
# POST request
@app.route("/accounts/register/", **crud("post"))
@app.route("/register", **crud("post"))
@api_response
def register():
    return register_resolver.resolve_for()


@app.route("/accounts/login", **crud("post"))
@api_response
def login():
    return login_resolver.resolve_for()


# refresh the JWT Token
# GET request
@app.route("/accounts/token/refresh/", **crud("get"))
@api_response
def refesh_token():
    return authentication_resolver.resolve_for()


# ===========================================================================
#                                  Users


# Get user info, secure data is removed for unauthenticated
# requests
@app.route("/accounts/<user_name>/", **crud("get", "patch", "delete"))
@api_response
def user_details(user_name):
    return user_resolver.resolve_for(user_name)


@app.route("/accounts/email-verification/", **crud("post", "patch"))
@api_response
def send_verification_email():
    return email_verification_resolver.resolve_for()


@app.route("/accounts/<user_name>/password/new/", **crud("post", "patch"))
@api_response
def send_password_reset_email(user_name):
    return paassword_reset_resolver.resolve_for()
