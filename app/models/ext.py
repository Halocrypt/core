from typing import Literal, Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


EventModel = Literal["main", "intra"]
DataR = TypeVar("DataR")


class RenderableContent(BaseModel):
    type: Literal["text", "link", "image-embed"]
    content: str


class UserSession(BaseModel):
    user: Optional[str]
    is_admin: Optional[bool]


class APIResponse(GenericModel, Generic[DataR]):
    data: DataR


class EmailRequest(BaseModel):
    handler: EventModel

    def get_subdomain(self):
        return "www" if self.handler == "main" else self.handler


class VerifyToken(BaseModel):
    token: str


class NewPassword(VerifyToken):
    new_password: str
