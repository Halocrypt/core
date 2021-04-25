from server.resolvers.base_resolver import BaseResolver
from server.api_handlers import admin, user
from server.util import ParsedRequest


class UserResolver(BaseResolver):
    def get(self, username):
        return user.get_user_details(ParsedRequest(), username)

    def patch(self, username):
        return user.edit(ParsedRequest(), username)

    def delete(self, username):
        return admin.delete(username)


class LoginResolver(BaseResolver):
    def post(self):
        return user.login(ParsedRequest())


class RegisterResolver(BaseResolver):
    def post(self):
        return user.register(ParsedRequest())


class AuthenticationResolver(BaseResolver):
    def get(self):
        return user.re_authenticate(ParsedRequest())


class EmailVerificationResolver(BaseResolver):
    def post(self):
        return user.send_verification_email(ParsedRequest())

    def patch(self):
        return user.confirm_email(ParsedRequest())


class PasswordResetResolver(BaseResolver):
    def post(self, username):
        return user.send_password_reset_email(ParsedRequest(), username)

    def patch(self, username):
        return user.verify_password_reset(ParsedRequest(), username)
