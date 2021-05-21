from app.db.models.base import Base
from typing import Optional, Union
from pydantic import BaseModel, constr, Field, EmailStr

from .ext import EventModel


class UserCreds(BaseModel):
    user: constr(strip_whitespace=True, to_lower=True, min_length=2, max_length=35)
    password: constr(min_length=4)


class UserRegister(UserCreds):
    name: constr(strip_whitespace=True)
    email: EmailStr
    institution: Optional[str]
    event: EventModel


class _UserSecure(BaseModel):
    email: EmailStr
    institution: Optional[str]
    has_verified_email: bool


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    user: str
    name: str
    created_at: int
    is_admin: bool = Field(False)
    is_disqualified: bool = Field(False)
    disqualification_reason: Optional[str]
    level: int
    points: int
    last_question_answered_at: int
    event: EventModel


class UserResponseSecure(UserResponse):
    secure: _UserSecure = Field(alias="_secure_")


class UserDetails(BaseModel):
    user_data: Union[UserResponseSecure, UserResponse]
