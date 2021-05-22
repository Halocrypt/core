from app.internal.constants import EVENT_NAMES
from app.internal.util import sanitize, validate_num
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import validates

from ..shared import assert_valid_event, raise_if_invalid_data
from .base import Base


class Question(Base):
    __tablename__ = "question"
    __mapper_args__ = {"eager_defaults": True}
    # pylint: disable=E1101

    _id = Column(String, primary_key=True)
    question_number = Column(Integer, nullable=False)
    question_points = Column(Integer, nullable=False)
    # intra|main
    event = Column(String(20), nullable=False)
    question_content = Column(JSONB, nullable=False)
    question_hints = Column(JSONB)
    # answers won't be longer than 100 characters, you heard it here first
    answer = Column(String(100), nullable=False)

    @validates("answer")
    def _validate_answer(self, key, val):
        return sanitize(val)

    @validates("question_points")
    def _validate_question_points(self, key, val):
        num = validate_num(val)
        if num <= 0:
            raise HTTPException(422, "Points should be greater than 0")
        return num

    @validates("question_content")
    def _validate_question_content(self, key, val):
        prefix = f"Error on question {self._id}:"
        if not isinstance(val, dict):
            raise HTTPException(
                422, f"{prefix} Please send a JSON object for the question"
            )

        t = val.get("type", "text")
        content = val.get("content")
        if t not in ("text", "link", "image-embed"):
            raise HTTPException(422, f"{prefix} invalid question content type")
        if not content:
            raise HTTPException(422, f"{prefix} Question content cannot be blank!")
        return {"type": t, "content": content}

    def __init__(
        self,
        question_number: int = None,
        question_points: int = None,
        event: str = None,
        question_content: dict = None,
        question_hints: list = None,
        answer: str = None,
    ):
        raise_if_invalid_data(question_points, event, question_content, answer)
        if question_number < 0 or question_points < 1:
            raise HTTPException(422, "Invalid question number/points")
        assert_valid_event(event)
        self._id = f"{event}:{question_number}"
        self.question_number = question_number
        self.question_points = question_points
        self.event = event
        self.question_content = question_content
        self.question_hints = question_hints
        self.answer = answer

    @property
    def as_json(self):
        return {
            "_id": self._id,
            "question_number": self.question_number,
            "question_points": self.question_points,
            "event": self.event,
            "question_content": self.question_content,
            "question_hints": self.question_hints,
            "_secure_": {"answer": self.answer},
        }

    # pylint: enable=E1101
