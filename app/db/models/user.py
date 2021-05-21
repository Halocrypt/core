from secrets import token_urlsafe
from time import time

from app.internal.constants import EVENT_NAMES
from app.internal.danger import generate_password_hash
from app.internal.util import sanitize, validate_email_address
from fastapi.exceptions import HTTPException
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import validates

from ..shared import raise_if_invalid_data
from .base import Base


class User(Base):
    __tablename__ = "user"
    __mapper_args__ = {"eager_defaults": True}
    # pylint: disable=E1101
    _id = Column(String(30), unique=True, nullable=False, primary_key=True)
    user = Column(String(35), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    institution = Column(String(100))
    password_hash = Column(String, nullable=False)
    created_at = Column(Integer)
    is_disqualified = Column(Boolean, default=False)
    disqualification_reason = Column(String, nullable=True)
    last_question_answered_at = Column(Integer)
    is_admin = Column(Boolean, default=False)
    level = Column(Integer, default=0)
    points = Column(Integer, default=0)
    has_verified_email = Column(Boolean)
    event = Column(String(10), nullable=False)
    # pylint: enable=E1101

    @property
    def as_json(self):
        return {
            "_id": self._id,
            "user": self.user,
            "name": self.name,
            "created_at": self.created_at,
            "is_admin": self.is_admin,
            "is_disqualified": self.is_disqualified,
            "disqualification_reason": self.disqualification_reason or None,
            "level": self.level,
            "points": self.points,
            "last_question_answered_at": self.last_question_answered_at,
            "event": self.event,
            "_secure_": {
                "email": self.email,
                "institution": self.institution,
                "has_verified_email": self.has_verified_email,
            },
        }

    @validates("name")
    def _validate_name(self, _, name):
        name = (name or "").strip()
        if not name:
            raise HTTPException(422, "name cannot be blank")
        return name

    @validates("user")
    def _validate_user(self, _, user):
        if not user:
            raise HTTPException(422, "Username cannot be blank")
        user = user.strip()
        length = len(user)
        if length > 30:
            raise HTTPException(422, "Username cannot be longer than 30 characters")
        if length < 3:
            raise HTTPException(422, "Username cannot be shorter than 3 characters")
        if sanitize(user) != user:
            raise HTTPException(
                422, "Username cannot have special characters or whitespace"
            )
        return user

    @validates("password_hash")
    def _validate_password(self, _, password):
        length = len(password)
        if length < 4:
            raise HTTPException(422, "Password cannot be shorter than 4 characters")
        return generate_password_hash(password)

    @validates("email")
    def _validate_email(self, _, email):
        email = email.strip() if email else None
        if not email:
            raise HTTPException(422, "Email cannot be blank")
        return validate_email_address(email)

    @validates("event")
    def _validate_event(self, _, event):
        if event not in EVENT_NAMES:
            raise HTTPException(422, "Invalid event")
        return event

    def __init__(
        self,
        user=None,
        name=None,
        email=None,
        institution=None,
        password=None,
        event=None,
    ):
        raise_if_invalid_data(user, name, password)
        self._id = token_urlsafe(15)
        self.user = user.lower()
        self.name = name
        self.email = email
        self.password_hash = password
        self.institution = institution
        self.event = event
        self.is_disqualified = False
        self.disqualification_reason = None
        self.is_admin = False
        self.created_at = time()
        self.level = 0
        self.points = 0
        self.last_question_answered_at = time()
        self.has_verified_email = False
