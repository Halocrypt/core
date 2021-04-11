from server.util import AppException
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from .shared import db, raise_if_invalid_data, EVENT_NAMES


class Question(db.Model):
    # pylint: disable=E1101

    _id = db.Column(db.String, primary_key=True)
    question_number = db.Column(db.Integer, nullable=False)
    question_points = db.Column(db.Integer, nullable=False)
    # intra|main
    event = db.Column(db.String(20), nullable=False)
    question_text = db.Column(db.String, nullable=False)
    question_hints = db.Column(MutableList.as_mutable(JSONB))
    # answers won't be longer than 100 characters, you heard it here first
    answer = db.Column(db.String(100), nullable=False)

    def __init__(
        self,
        question_number: int = None,
        question_points: int = None,
        event: str = None,
        question_text: str = None,
        question_hints: list = None,
        answer: str = None,
    ):
        raise_if_invalid_data(question_points, event, question_text, answer)
        if question_number < 0 or question_points < 1:
            raise AppException("Invalid question number/points")
        if event not in EVENT_NAMES:
            raise AppException("Invalid event value")
        self._id = f"{event}:{question_number}"
        self.question_number = question_number
        self.question_points = question_points
        self.event = event
        self.question_text = question_text
        self.question_hints = question_hints
        self.answer = answer

    @property
    def as_json(self):
        return {
            "_id": self._id,
            "question_number": self.question_number,
            "question_points": self.question_points,
            "event": self.event,
            "question_text": self.question_text,
            "question_hints": self.question_hints,
            "_secure_": {"answer": self.answer},
        }

    # pylint: enable=E1101
