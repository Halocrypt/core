from app.db.mutations import add_to_db
from app.db.models.question import Question
from app.models.play import ModifyQuestion, QuestionSecure
from app.internal.response_caching import cache, invalidate
from app.internal.webhooks import send_admin_action_webhook
from typing import List

from app.db.queries import (
    get_next_q_level,
    get_question_by_id,
    get_question_list,
    get_user_by_id,
    get_user_list,
)
from app.dependencies import inject_db, require_auth
from app.internal.api_response import api_response
from app.internal.router import Router
from app.models.admin import Disqualify
from app.models.ext import APIResponse, EventModel, UserSession
from app.models.user import UserResponseSecure
from fastapi import BackgroundTasks, Depends
from fastapi.exceptions import HTTPException

router = Router(tags=["admin"], dependencies=[Depends(require_auth.admin)])


@router.get(
    "/admin/{event}/users", response_model=APIResponse[List[UserResponseSecure]]
)
@api_response
async def get_all_users(event: EventModel, db=Depends(inject_db)):
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
    db=Depends(inject_db),
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
    db=Depends(inject_db),
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
async def add_question(event: EventModel, json: ModifyQuestion, db=Depends(inject_db)):
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
    event: EventModel, number: int, json: ModifyQuestion, db=Depends(inject_db)
):
    question = await get_question_by_id(db, event, number)
    question.question_content = json.question_content or question.question_content
    question.question_points = json.question_points or question.question_points
    question.question_hints = json.question_hints or question.question_hints
    question.answer = json.answer or question.answer
    js = question.as_json
    await db.commit()
    return invalidate([f"question-{event}-{number}", f"{event}-questions-list"], js)


@router.get(
    "/admin/events/{event}/questions/", response_model=APIResponse[List[QuestionSecure]]
)
@api_response
@cache(lambda event, **_: f"{event}-questions-list")
async def list_questions(event: EventModel, db=Depends(inject_db)):
    return [x.as_json for x in await get_question_list(db, event)]


@router.patch("/admin/events/{event}")
@api_response
def edit_event(event):
    return admin.edit_event(ParsedRequest(), event)


@router.get("/admin/yek-revresgol")
@api_response
def logserver_key():
    return admin.logserver_key()


@router.delete("/admin/{event}/notifications/<int:ts>")
@api_response
def delete_notification(event, ts):
    return admin.delete_notification(event, ts)


@router.patch("/admin/{event}/notifications")
@api_response
def add_notification(event):
    return admin.add_notification(ParsedRequest(), event)


@router.get("/admin/{event}/user-count")
@api_response
def user_count(event):
    return admin.user_count(event)


@router.get("/admin/-/invalidate")
@api_response
def invalidate_keys():
    return admin.invalidate_listener(ParsedRequest())