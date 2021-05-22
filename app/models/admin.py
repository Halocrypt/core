from typing import Optional
from pydantic import BaseModel, validator
from fastapi.exceptions import HTTPException


class Disqualify(BaseModel):
    reason: Optional[str]
    points: int

    @validator("points")
    def validate_points(cls, points):
        if points < 0:
            raise HTTPException(422, "You're adding points! Don't use negative symbol")
