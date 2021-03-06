from server.api_handlers.common import (
    add_to_db,
    delete_from_db,
    get_event_by_id,
    get_next_q_level,
    get_question_by_id,
    get_question_list,
    get_user_by_id,
    get_user_count,
    get_user_list,
    save_to_db,
    send_admin_action_webhook,
)
from server.api_handlers.cred_manager import CredManager
from server.auth_token import require_jwt
from server.constants import REMOTE_LOG_DB_KEY
from server.models.question import Question
from server.response_caching import cache, invalidate, invalidate_keys
from server.util import AppException, ParsedRequest, js_time
from sqlalchemy.orm.attributes import flag_modified


@require_jwt(admin_mode=True)
def event_users(event: str, creds=CredManager):
    return [x.as_json for x in get_user_list(event)]


@require_jwt(admin_mode=True)
def disqualify(req: ParsedRequest, user, *, creds: CredManager = CredManager):
    json = req.json
    reason = json.get("reason")
    deduct_points = json.get("points")
    if deduct_points < 0:
        raise AppException("You're adding points! Don't use negative symbol")
    user_data = get_user_by_id(user)
    if user_data.is_admin:
        raise AppException("Cannot disqualify an admin!")
    user_data.is_disqualified = True
    user_data.disqualification_reason = reason
    user_data.points -= deduct_points
    js = user_data.as_json
    send_admin_action_webhook([f"{user} was disqualified by {creds.user}"])
    save_to_db()
    return invalidate(f"{user_data.event}-leaderboard", js)


@require_jwt(admin_mode=True)
def requalify(user, creds=CredManager):
    user_data = get_user_by_id(user)
    user_data.is_disqualified = False
    user_data.disqualification_reason = None
    js = user_data.as_json
    save_to_db()
    send_admin_action_webhook([f"{user} was requalified by {creds.user}"])
    return invalidate(f"{user_data.event}-leaderboard", js)


@require_jwt(admin_mode=True)
def delete(user, creds: CredManager = CredManager):
    user_data = get_user_by_id(user)
    if user_data.is_admin:
        raise AppException("Cannot delete an admin account!")
    delete_from_db(user_data)
    send_admin_action_webhook([f"{user} was deleted by {creds.user}"])
    return {"success": True}


@require_jwt(admin_mode=True)
def add_question(req: ParsedRequest, event: str, creds=CredManager):
    return question_mutation(req.json, event)


@require_jwt(admin_mode=True)
def edit_question(req: ParsedRequest, event: str, number: int, creds=CredManager):
    return question_mutation(req.json, event, number)


@require_jwt(admin_mode=True)
@cache(lambda event, **_: f"{event}-questions-list")
def list_questions(event, creds=CredManager):
    return [x.as_json for x in get_question_list(event)]


def question_mutation(json: dict, event: str, question_number=None):
    points = json["question_points"]
    content = json["question_content"]
    hints = json["question_hints"]
    answer = json["answer"]
    if question_number is None:
        number = get_next_q_level(event)

        question = Question(
            question_number=number,
            question_points=points,
            event=event,
            question_content=content,
            question_hints=hints,
            answer=answer,
        )
        js = question.as_json
        add_to_db(question)
    else:
        question = get_question_by_id(event, question_number)
        question.question_points = points or question.points
        question.question_content = (
            content if content is not None else question.question_content
        )
        question.question_hints = (
            hints if hints is not None else question.question_hints
        )
        question.answer = answer or question.answer
        js = question.as_json
    save_to_db()
    return invalidate(
        [f"question-{event}-{question_number}", f"{event}-questions-list"], js
    )


@require_jwt(admin_mode=True)
def edit_event(req: ParsedRequest, event, creds=CredManager):
    ev = get_event_by_id(event)
    json = req.json

    start_time = json.get("event_start_time", ev.event_start_time)
    end_time = json.get("event_end_time", ev.event_end_time)
    is_over = json.get("is_over", ev.is_over)

    ev.event_start_time = start_time
    ev.event_end_time = end_time
    ev.is_over = is_over
    save_to_db()
    return invalidate(["events-list", f"{event}-event-details"], {"success": True})


@require_jwt(admin_mode=True)
def add_notification(req: ParsedRequest, event_name: str, creds=CredManager):
    event = get_event_by_id(event_name)
    notifs = event.notifications
    notifs.append({**req.json, "ts": js_time()})
    notifs.sort(key=lambda x: x["ts"], reverse=True)
    event.notifications = notifs
    flag_modified(event, "notifications")
    save_to_db()
    return invalidate(f"{event_name}-notifications", {"success": True})


@require_jwt(admin_mode=True)
def delete_notification(event_name: str, ts, creds=CredManager):
    event = get_event_by_id(event_name)
    notifs = event.notifications
    n = [x for x in notifs if x["ts"] != ts]
    n.sort(key=lambda x: x["ts"], reverse=True)
    event.notifications = n
    save_to_db()
    return invalidate(f"{event_name}-notifications", {"success": True})


@require_jwt(admin_mode=True)
@cache(lambda event, **_: f"{event}-user-count", timeout=20)
def user_count(event, creds=CredManager):
    return {"count": get_user_count(event)}


@require_jwt(admin_mode=True)
def logserver_key(creds=CredManager):

    return REMOTE_LOG_DB_KEY


def invalidate_listener(req: ParsedRequest):
    k = req.json["keys"]
    invalidate_keys(k)
    return {"success": True}
