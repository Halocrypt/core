from http import HTTPStatus
from secrets import token_urlsafe
from time import time


from server.danger import generate_password_hash
from server.util import AppException, sanitize, validate_email_address
from sqlalchemy.orm import validates

from .shared import db, raise_if_invalid_data


class UserTable(db.Model):
    # pylint: disable=E1101
    _id: str = db.Column(db.String(30), unique=True, nullable=False, primary_key=True)
    user: str = db.Column(db.String(30), unique=True, nullable=False)
    name: str = db.Column(db.String(30), nullable=False)
    email: str = db.Column(db.String(250), nullable=False, unique=True)
    institution: str = db.Column(db.String(100))
    password_hash: str = db.Column(db.String, nullable=False)
    created_at: int = db.Column(db.Integer)
    is_disqualified: bool = db.Column(db.Boolean, default=False)
    disqualification_reason: bool = db.Column(db.String, nullable=True)
    last_question_answered_at: int = db.Column(db.Integer)
    is_admin: bool = db.Column(db.Boolean, default=False)
    level: int = db.Column(db.Integer, default=0)
    points: int = db.Column(db.Integer, default=0)
    has_verified_email: bool = db.Column(db.Boolean)
    # pylint: enable=E1101

    @property
    def as_json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "user": self.user,
            "created_at": self.created_at,
            "is_admin": self.is_admin,
            "is_disqualified": self.is_disqualified,
            "disqualification_reason": self.disqualification_reason or None,
            "level": self.level,
            "points": self.points,
            "last_question_answered_at": self.last_question_answered_at,
            "_secure_": {
                "email": self.email,
                "institution": self.institution,
                "has_verified_email": self.has_verified_email,
            },
        }

    @validates("user")
    def _validate_user(self, key, user: str):
        if not user:
            raise AppException(
                "Username cannot be blank", HTTPStatus.UNPROCESSABLE_ENTITY
            )
        user = user.strip()
        length = len(user)
        if length > 30:
            raise AppException(
                "Username cannot be longer than 30 characters",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        if length < 3:
            raise AppException(
                "Username cannot be shorter than 3 characters",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        if sanitize(user) != user:
            raise AppException(
                "Username cannot have special characters or whitespace",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        return user

    @validates("password_hash")
    def _validate_password(self, key, password: str):
        length = len(password)
        if length < 4:
            raise AppException("Password cannot be shorter than 4 characters")
        return generate_password_hash(password)

    @validates("email")
    def _validate_email(self, key, email: str):
        email = email.strip() if email else None
        if not email:
            raise AppException("Email cannot be blank")
        return validate_email_address(email)

    def __init__(
        self,
        user: str = None,
        name: str = None,
        email: str = None,
        institution: str = None,
        password: str = None,
    ):
        raise_if_invalid_data(user, name, password)
        self._id = token_urlsafe(20)
        self.user = user.lower()
        self.name = name
        self.email = email
        self.password_hash = password
        self.institution = institution
        self.is_disqualified = False
        self.is_admin = False
        self.created_at = time()
        self.level = 0
        self.points = 0
        self.last_question_answered_at = time()
