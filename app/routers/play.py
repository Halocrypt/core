from time import time
from typing import List, Union


from app.db.queries import (
    assert_hunt_running,
    get_event_by_id,
    get_events_list,
    get_leaderboard,
    get_question,
    get_user_by_id,
)
from app.dependencies import inject_db, require_auth
from app.internal.api_response import api_response
from app.internal.response_caching import cache, invalidate
from app.internal.router import Router
from app.internal.util import log_answer, sanitize
from app.models.ext import APIResponse, EventModel, UserSession
from app.models.play import (
    Answer,
    AnswerEvaluation,
    DQResponse,
    GameOverResponse,
    Leaderboard,
    Notifications,
    QuestionResponse,
)
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

router = Router(tags=["user"])
from app.internal.router import Router

router = Router(tags=["play"])

Q = APIResponse[Union[QuestionResponse, DQResponse, GameOverResponse]]
A = APIResponse[Union[AnswerEvaluation, DQResponse, GameOverResponse]]


@router.get("/play/{event}/leaderboard", response_model=APIResponse[List[Leaderboard]])
@api_response
@cache(lambda event, **_: f"{event}-leaderboard")
async def leaderboard(event: EventModel, db: AsyncSession = Depends(inject_db)):
    return await get_leaderboard(db, event)


@router.get("/play/{event}/question", response_model=Q)
@api_response
async def question(
    event: EventModel,
    db: AsyncSession = Depends(inject_db),
    auth: UserSession = Depends(require_auth),
):
    await assert_hunt_running(db, event)
    user_data = await get_user_by_id(db, auth.user)
    if user_data.event != event:
        raise HTTPException(403, "Not your event")
    if user_data.is_disqualified:
        return {"disqualified": True, "reason": user_data.disqualification_reason}
    try:
        try:
            q = await get_question(db, event, user_data.level)
        except HTTPException:
            return {"game_over": True}
        return q
    except:
        raise HTTPException(500, "Unknown error occured")


@router.post("/play/{event}/answer", response_model=A)
@api_response
async def answer(
    event: EventModel,
    json: Answer,
    db: AsyncSession = Depends(inject_db),
    auth: UserSession = Depends(require_auth),
):
    await assert_hunt_running(db, event)
    answer = json.answer
    if not answer:
        return {"is_correct": False}
    user_data = await get_user_by_id(db, auth.user)
    if user_data.event != event:
        raise HTTPException(403, "Not your event..")
    if user_data.is_disqualified:
        return {"disqualified": True, "reason": user_data.disqualification_reason}
    try:
        try:
            q = await get_question(db, event, user_data.level)
        except HTTPException:
            return {"game_over": True}
        is_correct = sanitize(q["_secure_"]["answer"]) == answer
        log_answer(user_data.user, q["question_number"], answer, is_correct)
        if is_correct:
            user_data.level += 1
            user_data.points += q["question_points"]
            user_data.last_question_answered_at = time()
            await db.commit()
            return invalidate(f"{event}-leaderboard", {"is_correct": True})
        return {"is_correct": False}

    except Exception as e:
        print(e)
        raise HTTPException(500, "An unknown error occured")


@router.get(
    "/play/{event}/notifications", response_model=APIResponse[List[Notifications]]
)
@api_response
@cache(lambda event, **a: f"{event}-notifications", timeout=5 * 60 * 60)
async def get_notifications(
    event: EventModel,
    db: AsyncSession = Depends(inject_db),
):
    ev = await get_event_by_id(db, event)
    return ev.notifications


@router.get("/play/events")
@api_response
@cache("events-list")
async def list_events(db: AsyncSession = Depends(inject_db)):
    return await get_events_list(db)
