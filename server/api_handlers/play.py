from http import HTTPStatus
from logserver.app import LOGSERVER_KEY
from server.constants import BOT_ACCESS_KEY
from server.response_caching import cache
from time import time

import requests

from server.api_handlers.common import (
    clean_secure,
    get_event_details,
    get_question,
    get_user_by_id,
    get_user_count,
    save_to_db,
)
from server.api_handlers.cred_manager import CredManager
from server.auth_token import require_jwt
from server.util import js_time, sanitize
from server.models.user import User
from server.util import AppException, ParsedRequest


@cache(lambda x: f"{x}-leaderboard", 30)
def leaderboard(x):
    users = User.query.order_by(
        User.is_disqualified.asc(),
        User.is_admin.asc(),
        User.points.desc(),
        User.level.desc(),
        User.last_question_answered_at.asc(),
    ).filter_by(event=x)

    return [clean_secure(x) for x in users.all()]


@require_jwt()
def question(event, creds: CredManager = CredManager):
    is_hunt_running(event)
    user = get_user_by_id(creds.user)
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
    is_hunt_running(event)
    js = req.json
    answer = sanitize(js.get("answer", ""))
    # don't even bother if the user is trying an absurdly large answer
    if len(answer) > 50 or not answer:
        return {"is_correct": False}

    user = get_user_by_id(creds.user)
    if user.is_disqualified:
        return {"disqualified": True, "reason": user.disqualification_reason}
    try:
        try:
            q = get_question(event, user.level)
        except AppException:
            return {"game_over": True}
        is_correct = sanitize(q["_secure_"]["answer"]) == answer
        if is_correct:
            user.level += 1
            user.points += q["question_points"]
            user.last_question_answered_at = time()
            log_answer(user.user, q["question_number"], js["answer"], is_correct)
            save_to_db()
        return {"is_correct": is_correct}

    except Exception as e:
        print(e)
        raise Exception("An unknown error occured")


def user_count(req: ParsedRequest, event):
    if req.headers.get("x-access-key") != BOT_ACCESS_KEY:
        raise AppException("No", HTTPStatus.FORBIDDEN)
    return get_user_count(event)


def is_hunt_running(event):
    ev = get_event_details(event)
    curr_time = time()
    has_not_started = ev["event_start_time"] > curr_time
    is_over = ev["is_over"] or ev["event_end_time"] < curr_time
    if is_over:
        raise AppException("Hunt is over", HTTPStatus.FORBIDDEN)
    if has_not_started:
        raise AppException("Hunt hasn't started yet..", HTTPStatus.FORBIDDEN)


def log_answer(user, question, answer, is_correct):
    requests.post(
        "http://localhost:5001/log/cf",
        headers={"x-logserver-key": LOGSERVER_KEY},
        json=[user, question, answer, is_correct, js_time()],
    )
