from app.internal.util import js_time
from typing import List

from sqlalchemy.orm.attributes import flag_modified

from app.db.models.question import Question
from app.db.mutations import add_to_db
from app.db.queries import (
    get_event_by_id,
    get_next_q_level,
    get_question_by_id,
    get_question_list,
    get_user_by_id,
    get_user_count,
    get_user_list,
)
from app.dependencies import inject_db, require_auth
from app.internal.api_response import api_response
from app.internal.constants import REMOTE_LOG_DB_KEY
from app.internal.response_caching import cache, invalidate, invalidate_keys
from app.internal.router import Router
from app.internal.webhooks import send_admin_action_webhook
from app.models.admin import Disqualify
from app.models.ext import APIResponse, EventModel, UserSession
from app.models.play import ModifyQuestion, Notifications, QuestionSecure
from app.models.user import UserResponseSecure
from fastapi import BackgroundTasks, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

router = Router(tags=["admin"], dependencies=[Depends(require_auth.admin)])


@router.get(
    "/admin/{event}/users", response_model=APIResponse[List[UserResponseSecure]]
)
@api_response
async def get_all_users(event: EventModel, db: AsyncSession = Depends(inject_db)):
    return [x.as_json for x in await get_user_list(db, event)]


@router.patch(
    "/admin/accounts/{user}/disqualify",
    response_model=APIResponse[UserResponseSecure],
)
@api_response
async def disqualify(
    user: str,
    json: Disqualify,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(inject_db),
    auth: UserSession = Depends(require_auth.admin),
):
    reason = json.reason
    points = json.points
    user_data = await get_user_by_id(db, user)
    if user_data.is_admin:
        raise HTTPException(403, "Cannot disqualify an admin!")
    user_data.is_disqualified = True
    user_data.disqualification_reason = reason
    user_data.points -= points
    js = user_data.as_json
    background_tasks.add_task(
        send_admin_action_webhook, [f"{user} was disqualified by {auth.user}"]
    )
    await db.commit()
    return invalidate(f"{js['event']}-leaderboard", js)


@router.patch(
    "/admin/accounts/{user}/requalify",
    response_model=APIResponse[UserResponseSecure],
)
@api_response
async def requalify(
    user: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(inject_db),
    auth: UserSession = Depends(require_auth.admin),
):
    user_data = await get_user_by_id(db, user)
    user_data.is_disqualified = False
    user_data.disqualification_reason = None
    js = user_data.as_json
    await db.commit()
    background_tasks.add_task(
        send_admin_action_webhook, [f"{user} was requalified by {auth.user}"]
    )
    return invalidate(f"{js['event']}-leaderboard", js)


@router.post(
    "/admin/{event}/questions/add/", response_model=APIResponse[QuestionSecure]
)
@api_response
async def add_question(
    event: EventModel, json: ModifyQuestion, db: AsyncSession = Depends(inject_db)
):
    number = await get_next_q_level(db, event)
    question = Question(question_number=number, event=event, **json.dict())
    js = question.as_json
    await add_to_db(db, question)
    return invalidate([f"question-{event}-{number}", f"{event}-questions-list"], js)


@router.patch(
    "/admin/{event}/questions/{number}/", response_model=APIResponse[QuestionSecure]
)
@api_response
async def edit_questions(
    event: EventModel,
    number: int,
    json: ModifyQuestion,
    db: AsyncSession = Depends(inject_db),
):
    question = await get_question_by_id(db, event, number)
    data = json.dict()
    question.question_content = data["question_content"] or question.question_content
    question.question_points = data["question_points"] or question.question_points
    question.question_hints = data["question_hints"] or question.question_hints
    question.answer = data["answer"] or question.answer
    js = question.as_json
    await db.commit()
    return invalidate([f"question-{event}-{number}", f"{event}-questions-list"], js)


@router.get(
    "/admin/events/{event}/questions/", response_model=APIResponse[List[QuestionSecure]]
)
@api_response
@cache(lambda event, **_: f"{event}-questions-list")
async def list_questions(event: EventModel, db: AsyncSession = Depends(inject_db)):
    return [x.as_json for x in await get_question_list(db, event)]


@router.patch("/admin/events/{event}")
@api_response
async def edit_event(
    event: EventModel, json: dict, db: AsyncSession = Depends(inject_db)
):
    ev = await get_event_by_id(db, event)
    start_time = json.get("event_start_time", ev.event_start_time)
    end_time = json.get("event_end_time", ev.event_end_time)
    is_over = json.get("is_over", ev.is_over)
    ev.event_start_time = start_time
    ev.event_end_time = end_time
    ev.is_over = is_over
    await db.commit()
    return invalidate(["events-list", f"{event}-event-details"], {"success": True})


@router.get("/admin/yek-revresgol")
@api_response
async def logserver_key():
    return REMOTE_LOG_DB_KEY


@router.patch("/admin/{event}/notifications")
@api_response
async def add_notification(
    event: EventModel, req: Notifications, db: AsyncSession = Depends(inject_db)
):
    event_data = await get_event_by_id(db, event)
    notifs = event_data.notifications
    notifs.append({**req.dict(), "ts": js_time()})
    notifs.sort(key=lambda x: x["ts"], reverse=True)
    event_data.notifications = notifs
    flag_modified(event_data, "notifications")
    await db.commit()
    return invalidate(f"{event}-notifications", {"success": True})


@router.delete("/admin/{event}/notifications/{ts}")
@api_response
async def delete_notification(
    event: EventModel, ts: int, db: AsyncSession = Depends(inject_db)
):
    event_data = await get_event_by_id(db, event)
    notifs = event_data.notifications
    n = [x for x in notifs if x["ts"] != ts]
    n.sort(key=lambda x: x["ts"], reverse=True)
    event_data.notifications = n
    await db.commit()
    return invalidate(f"{event}-notifications", {"success": True})


@router.get("/admin/{event}/user-count")
@api_response
@cache(lambda event, **_: f"{event}-user-count", timeout=20)
async def user_count(event: EventModel, db: AsyncSession = Depends(inject_db)):
    return {"count": await get_user_count(db, event)}


@router.get("/admin/-/invalidate", include_in_schema=False)
@api_response
async def invalidate_local_cache(json: dict):
    invalidate_keys(json["keys"])
    return {"success": True}
