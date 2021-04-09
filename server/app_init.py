from secrets import token_urlsafe
from time import time

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from floodgate import guard
from sqlalchemy.orm import validates

from .constants import DATABASE_URL, FLASK_SECRET, IS_PROD
from .danger import generate_password_hash
from .util import (
    AppException,
    get_origin,
    json_response,
    sanitize,
    validate_email_address,
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET
database_url: str = DATABASE_URL

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.before_request
@guard(ban_time=5, ip_resolver="heroku" if IS_PROD else None, request_count=50, per=15)
def gate_check():
    pass


@app.errorhandler(404)
def catch_all(e):
    return json_response({"error": "not found"})


@app.errorhandler(405)
def method_not_allowed(e):
    return json_response({"error": "Method not allowed"})


EXPOSE_HEADERS = ", ".join(("x-access-token", "x-refresh-token", "x-dynamic"))


@app.after_request
def cors(resp):
    origin = get_origin(request)
    resp.headers["access-control-allow-origin"] = origin
    resp.headers["access-control-allow-headers"] = request.headers.get(
        "access-control-request-headers", "*"
    )
    resp.headers["access-control-allow-credentials"] = "true"
    resp.headers["x-dynamic"] = "true"
    resp.headers["access-control-max-age"] = "86400"
    resp.headers["access-control-expose-headers"] = EXPOSE_HEADERS
    return resp


class UserTable(db.Model):
    # pylint: disable=E1101
    _id: str = db.Column(db.String(30), unique=True, nullable=False, primary_key=True)
    user: str = db.Column(db.String(30), unique=True, nullable=False)
    name: str = db.Column(db.String(30), nullable=False)
    email: str = db.Column(db.String(250), nullable=False, unique=True)
    institution: str = db.Column(db.String(100))
    password_hash: str = db.Column(db.String, nullable=False)
    created_at: int = db.Column(db.Integer)
    # pylint: enable=E1101

    @property
    def as_json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "user": self.user,
            "created_at": self.created_at,
            "_secure_": {"email": self.email, "institution": self.institution},
        }

    @validates("user")
    def _validate_user(self, key, user: str):
        if not user:
            raise AppException("Username cannot be blank")
        user = user.strip()
        length = len(user)
        if length > 30:
            raise AppException("Username cannot be longer than 30 characters")
        if length < 4:
            raise AppException("Username cannot be shorter than 4 characters")
        if sanitize(user) != user:
            raise AppException("Username cannot have special characters or whitespace")
        return user

    @validates("password_hash")
    def _validate_password(self, key, password: str):
        length = len(password)
        if length < 4:
            raise AppException("Password cannot be shorter than 4 characters")
        return generate_password_hash(password)

    @validates("email")
    def _validate_email(self, key, email: str):
        if email:
            raise AppException("Email cannot be blank")
        email = email.strip()
        return validate_email_address(email)

    def __init__(
        self,
        user: str = None,
        name: str = None,
        email: str = None,
        password: str = None,
    ):
        raise_if_invalid_data(user, name, password)
        self._id = token_urlsafe(20)
        self.user = user.lower()
        self.name = name
        self.email = email
        self.password_hash = password
        self.created_at = time()


def raise_if_invalid_data(*args):
    if any(not x or not ((x).strip() if isinstance(x, str) else True) for x in args):
        raise AppException("Invalid Input")
