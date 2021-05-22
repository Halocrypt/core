from time import time

from fastapi.exceptions import HTTPException
from app.models.play import Leaderboard
from app.internal.response_caching import cache
from app.db.models.event import Event
from sqlalchemy import func
from app.db.models.question import Question
from app.models.ext import EventModel
from app.db.shared import assert_exists, assert_valid_event, get_one, get_all
from sqlalchemy import select

from app.db.models import User
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.util import sanitize


async def get_user_by_id(db: AsyncSession, username: str) -> User:
    username = (username or "").lower()
    if not username or sanitize(username) != username:
        return assert_exists(None)
    stmt = select(User).where(User.user == username)
    q = await db.execute(stmt)
    return assert_exists(get_one(q))


async def get_question_by_id(
    db: AsyncSession, event: EventModel, number: int
) -> Question:
    assert_valid_event(event)
    if number < 0:
        return assert_exists(None, "Question")
    stmt = select(Question).where(Question._id == f"{event}:{number}")
    q = await db.execute(stmt)
    return assert_exists(get_one(q), "Question")


async def get_latest_q_level(db: AsyncSession, event: EventModel) -> int:
    assert_valid_event(event)
    stmt = select(func.max(Question.question_number)).where(Question.event == event)
    q = await db.execute(stmt)
    return get_one(q)


async def get_next_q_level(db: AsyncSession, event: EventModel) -> int:
    t = await get_latest_q_level(db, event)
    return t + 1 if t is not None else 0


async def get_user_list(db: AsyncSession, event: EventModel) -> List[User]:
    stmt = (
        select(User)
        .where(User.event == event)
        .order_by(User.is_disqualified.desc(), User.user.asc())
    )
    q = await db.execute(stmt)
    return get_all(q)


async def get_question_list(db: AsyncSession, event: EventModel) -> List[Question]:
    stmt = (
        select(Question)
        .where(Question.event == event)
        .order_by(Question.question_number.asc())
    )
    q = await db.execute(stmt)
    return get_all(q)


async def get_event_by_id(db: AsyncSession, event: EventModel) -> Event:
    assert_valid_event(event)
    stmt = select(Event).where(Event.name == event)
    q = await db.execute(stmt)
    return get_one(q)


async def get_events_list(db: AsyncSession) -> List[dict]:
    stmt = select(Event).order_by(Event.name.desc())
    q = await db.execute(stmt)
    return [x.as_json for x in get_all(q)]


async def get_user_count(db: AsyncSession, event: Event) -> int:
    assert_valid_event(event)
    stmt = select(func.count(User._id)).where(User.event == event)
    q = await db.execute(stmt)
    return q.scalars().first()


@cache(lambda db, event: f"{event}-event-details", json_cache=True)
async def get_event_details(db: AsyncSession, event: Event) -> dict:
    ev = await get_event_by_id(db, event)
    return ev.as_json


@cache(lambda db, event, number: f"question-{event}-{number}", json_cache=True)
async def get_question(db: AsyncSession, event: Event, number: int) -> dict:
    q = await get_question_by_id(db, event, number)
    return q.as_json


async def get_leaderboard(db: AsyncSession, event: Event) -> List[dict]:
    stmt = (
        select(User)
        .order_by(
            User.is_disqualified.asc(),
            User.is_admin.asc(),
            User.points.desc(),
            User.level.desc(),
            User.last_question_answered_at.asc(),
        )
        .where(User.event == event)
    )
    q = await db.execute(stmt)
    return [Leaderboard(**x.as_json).dict() for x in get_all(q)]


async def assert_hunt_running(db: AsyncSession, event: str):
    ev = await get_event_details(db, event)
    curr_time = time()
    has_not_started = ev["event_start_time"] > curr_time
    is_over = ev["is_over"] or ev["event_end_time"] < curr_time
    if is_over:
        raise HTTPException(403, "Hunt is over")
    if has_not_started:
        raise HTTPException(403, "Hunt hasn't started yet..")
