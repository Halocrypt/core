from typing import List, Optional


from pydantic import BaseModel, validator, Field
from app.internal.util import sanitize
from .ext import EventModel, RenderableContent


class Leaderboard(BaseModel):
    user: str
    name: str
    points: int
    level: int
    is_admin: bool
    is_disqualified: bool


class QuestionBase(BaseModel):
    question_points: Optional[int] = Field(gt=0)
    question_content: Optional[RenderableContent]
    question_hints: Optional[List[RenderableContent]]


class QuestionResponse(QuestionBase):
    id: str = Field(alias="_id")
    question_number: int
    event: EventModel


class _SecAnswer(BaseModel):
    answer: str


class QuestionSecure(QuestionResponse):
    secure: _SecAnswer = Field(alias="_secure_")


class ModifyQuestion(QuestionBase):
    answer: Optional[str]


class DQResponse(BaseModel):
    disqualified: bool
    reason: bool


class GameOverResponse(BaseModel):
    game_over: bool


class Answer(BaseModel):
    answer: str

    @validator("answer")
    # pylint: disable=E0213
    def validate_answer(cls, ans):
        ret = sanitize(ans) if ans else None
        if not ret or len(ret) > 50:
            return ""
        return ans


class AnswerEvaluation(BaseModel):
    is_correct: bool


class Notifications(BaseModel):
    ts: int
    title: str
    content: RenderableContent
    issuedBy: str
