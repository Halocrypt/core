from server.constants import NOTIFICATION_KEY
from server.models.question import Question
from server.api_handlers.common import (
    add_to_db,
    delete_from_db,
    get_event_by_id,
    get_next_q_level,
    get_question_by_id,
    get_questions,
    get_user_by_id,
    save_to_db,
)
from server.api_handlers.cred_manager import CredManager
from server.util import AppException, ParsedRequest

from server.auth_token import require_jwt
from server.response_caching import invalidate


@require_jwt(admin_mode=True)
def disqualify(req: ParsedRequest, user, *, creds: CredManager = CredManager):
    json = req.json
    reason = json.get("reason")
    deduct_points = json.get("points")
    if deduct_points < 0:
        raise AppException("You're adding points! Don't use negative symbol")
    user_data = get_user_by_id(user)
    user_data.is_disqualified = True
    user_data.disqualification_reason = reason
    user_data.points -= deduct_points
    js = user_data.as_json
    invalidate(f"{user_data.event}-leaderboard")
    save_to_db()
    return js


@require_jwt(admin_mode=True)
def requalify(user, creds=CredManager):
    user_data = get_user_by_id(user)
    user_data.is_disqualified = False
    user_data.disqualification_reason = None
    js = user_data.as_json
    invalidate(f"{user_data.event}-leaderboard")
    save_to_db()
    return js


@require_jwt(admin_mode=True)
def delete(user, creds: CredManager = CredManager):
    user_data = get_user_by_id(user)
    delete_from_db(user_data)
    return {"success": True}


@require_jwt(admin_mode=True)
def add_question(req: ParsedRequest, event: str, creds=CredManager):
    return question_mutation(req.json, event)


@require_jwt(admin_mode=True)
def edit_question(req: ParsedRequest, event: str, number: int, creds=CredManager):
    return question_mutation(req.json, event, number)


@require_jwt(admin_mode=True)
def list_questions(event, creds=CredManager):
    return [x.as_json for x in get_questions(event)]


def question_mutation(json: dict, event: str, question_number=None):
    points = json["points"]
    text = json.get("question_text")
    hints = json.get("hints")
    answer = json.get("answer")
    if question_number is None:
        number = get_next_q_level(event)

        question = Question(
            question_number=number,
            question_points=points,
            event=event,
            question_text=text,
            question_hints=hints,
            answer=answer,
        )
        js = question.as_json
        add_to_db(question)
    else:
        question = get_question_by_id(event, question_number)
        question.question_points = points or question.points
        question.question_text = text or question.question_text
        question.question_hints = hints or question.question_hints
        question.answer = answer or question.answer
        js = question.as_json
        invalidate(f"question-{event}-{question_number}")
    save_to_db()
    return js


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

    invalidate(f"{event}-event-details")
    save_to_db()
    return {"success": True}


@require_jwt(admin_mode=True)
def notification_key(creds=CredManager):
    return NOTIFICATION_KEY