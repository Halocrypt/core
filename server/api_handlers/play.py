from http import HTTPStatus
from server.constants import (
    IS_PROD,
    LOG_SERVER_ENDPOINT,
    MIN_QUESTION_TO_LOG,
    REMOTE_LOG_DB_KEY,
)
from server.response_caching import cache, invalidate
from time import time

import requests

from server.api_handlers.common import (
    get_event_by_id,
    get_event_details,
    get_events_list,
    get_question,
    get_user_by_id,
    save_to_db,
    send_level_solved_webhook,
)
from server.api_handlers.cred_manager import CredManager
from server.auth_token import require_jwt
from server.util import js_time, only_keys, sanitize
from server.models.user import User
from server.util import AppException, ParsedRequest


leaderboard_keys = ("user", "name", "points", "level", "is_admin", "is_disqualified")


@cache(lambda x: f"{x}-leaderboard")
def leaderboard(x):
    users = User.query.order_by(
        User.is_disqualified.asc(),
        User.is_admin.asc(),
        User.points.desc(),
        User.level.desc(),
        User.last_question_answered_at.asc(),
    ).filter_by(event=x)

    return [only_keys(x.as_json, *leaderboard_keys) for x in users.all()]


@require_jwt()
def question(event, creds: CredManager = CredManager):
    assert_hunt_running(event)
    user = get_user_by_id(creds.user)
    if user.event != event:
        raise AppException("Not your event..")
    if user.is_disqualified:
        return {"disqualified": True, "reason": user.disqualification_reason}
    try:
        try:
            q = get_question(event, user.level)
        except AppException:
            return {"game_over": True}
        q.pop("_secure_")
        return q
    except:
        raise Exception("Unknown error occured")


@require_jwt()
def answer(req: ParsedRequest, event, creds: CredManager = CredManager):
    assert_hunt_running(event)
    js = req.json
    answer = sanitize(js.get("answer", ""))
    # don't even bother if the user is trying an absurdly large answer
    if len(answer) > 50 or not answer:
        return {"is_correct": False}
    user = get_user_by_id(creds.user)
    if user.event != event:
        raise AppException("Not your event..")
    if user.is_disqualified:
        return {"disqualified": True, "reason": user.disqualification_reason}
    try:
        try:
            q = get_question(event, user.level)
        except AppException:
            return {"game_over": True}
        is_correct = sanitize(q["_secure_"]["answer"]) == answer
        log_answer(user.user, q["question_number"], js["answer"], is_correct)
        if is_correct:
            user.level += 1
            user.points += q["question_points"]
            user.last_question_answered_at = time()
            save_to_db()
            return invalidate(f"{event}-leaderboard", {"is_correct": is_correct})
        return {"is_correct": is_correct}

    except Exception as e:
        print(e)
        raise Exception("An unknown error occured")


def assert_hunt_running(event):
    ev = get_event_details(event)
    curr_time = time()
    has_not_started = ev["event_start_time"] > curr_time
    is_over = ev["is_over"] or ev["event_end_time"] < curr_time
    if is_over:
        raise AppException("Hunt is over", HTTPStatus.FORBIDDEN)
    if has_not_started:
        raise AppException("Hunt hasn't started yet..", HTTPStatus.FORBIDDEN)


def log_answer(user, question, answer, is_correct):
    if question >= MIN_QUESTION_TO_LOG and IS_PROD:
        requests.post(
            f"{LOG_SERVER_ENDPOINT}/add",
            headers={"x-access-key": REMOTE_LOG_DB_KEY},
            json=[user, question, answer, is_correct, js_time()],
        )
        if is_correct:
            send_level_solved_webhook(user, question, answer)


@require_jwt()
@cache(lambda x, **_: f"{x}-notifications", timeout=5 * 60 * 60)
def get_notifications(x, creds=CredManager):
    return get_event_by_id(x).notifications


@cache("events-list")
def list_events():
    return get_events_list()
