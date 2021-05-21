from server.constants import EVENT_NAMES
from server.util import AppException, sanitize, validate_num
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import validates

from .shared import db, raise_if_invalid_data


class Question(db.Model):
    # pylint: disable=E1101

    _id = db.Column(db.String, primary_key=True)
    question_number = db.Column(db.Integer, nullable=False)
    question_points = db.Column(db.Integer, nullable=False)
    # intra|main
    event = db.Column(db.String(20), nullable=False)
    question_content = db.Column(JSONB, nullable=False)
    question_hints = db.Column(JSONB)
    # answers won't be longer than 100 characters, you heard it here first
    answer = db.Column(db.String(100), nullable=False)

    @validates("answer")
    def _validate_answer(self, key, val):
        return sanitize(val)

    @validates("question_points")
    def _validate_question_points(self, key, val):
        num = validate_num(val)
        if num <= 0:
            raise AppException("Points should be greater than 0")
        return num

    @validates("question_content")
    def _validate_question_content(self, key, val):
        prefix = f"Error on question {self._id}:"
        if not isinstance(val, dict):
            raise AppException(f"{prefix} Please send a JSON object for the question")

        t = val.get("type", "text")
        if t not in ("text", "link", "image-embed"):
            raise AppException(f"{prefix} invalid question content type")
        if not val.get("content"):
            raise AppException(f"{prefix} Question content cannot be blank!")
        return {"type": val["type"], "content": val["content"]}

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
            raise AppException("Invalid question number/points")
        if event not in EVENT_NAMES:
            raise AppException("Invalid event value")
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
