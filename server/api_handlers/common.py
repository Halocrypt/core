from http import HTTPStatus
from server.response_caching import cache
from typing import List
from sqlalchemy import func as _func
import requests

from server.models import User as _U, Question as _Q, Event as _E
from server.models import db as _db
from server.util import AppException as _AppException
from server.util import sanitize
from server.constants import EVENT_NAMES, BACKEND_WEBHOOK_URL

lower = _func.lower
count = _func.count


# pylint: disable=E1101
def add_to_db(data, batch=False):
    _db.session.add(data)
    not batch and save_to_db()


def clean_secure(x):
    js = x.as_json
    js.pop("_secure_")
    return js


def save_to_db():
    _db.session.commit()


def delete_from_db(d, batch=False):
    if d:
        _db.session.delete(d)
        not batch and save_to_db()


def get_user_by_id(idx: str) -> _U:
    idx = (idx or "").lower()
    if not idx or sanitize(idx) != idx:
        return _assert_exists(None)
    return _assert_exists(_U.query.filter(lower(_U.user) == lower(idx)).first())


def get_question_by_id(event: str, number: int) -> _Q:
    if number < 0:
        return _assert_exists(None, "Question")
    q = _assert_exists(_Q.query.filter_by(_id=f"{event}:{number}").first(), "Question")
    return q


def get_latest_q_level(event: str) -> int:
    _assert_exists(event or None, "Event")
    t = _func.max(_Q.question_number)
    curr = _db.session.query(t).filter(_Q.event == event).first()[0]
    return curr


def get_next_q_level(event: str) -> int:
    t = get_latest_q_level(event)
    return t + 1 if t is not None else 0


def get_user_list(event: str) -> List[_U]:
    return _U.query.order_by(_U.user.asc()).filter_by(event=event).all()


def get_question_list(event: str) -> List[_Q]:
    return _Q.query.order_by(_Q.question_number.asc()).filter_by(event=event).all()


def get_event_by_id(event: str) -> _E:
    if event not in EVENT_NAMES:
        return _assert_exists(None, "Event")
    return _assert_exists(_E.query.filter_by(name=event).first(), "Event")


def get_events_list():
    return [x.as_json for x in _E.query.order_by(_E.name.desc()).all()]


def get_user_count(event):
    return _db.session.query(_U).filter_by(event=event).count()


def _assert_exists(user: _U, name="User"):
    if user is None:
        raise _AppException(f"{name} does not exist", HTTPStatus.NOT_FOUND)
    return user


@cache(lambda event: f"{event}-event-details", json_cache=True)
def get_event_details(event):
    ev = get_event_by_id(event)
    return ev.as_json


@cache(lambda event, number: f"question-{event}-{number}", json_cache=True)
def get_question(event, number):
    q = get_question_by_id(event, number)
    return q.as_json


def send_webhook(url, json):
    return
    # return requests.post(url, json={**json, "allowed_mentions": {"parse": []}})


def get_webhook_json(title, description, color):
    return {"embeds": [{"title": title, "description": description, "color": color}]}


def send_level_solved_webhook(user, level, answer):
    send_webhook(
        BACKEND_WEBHOOK_URL,
        get_webhook_json(
            f"Level Solved",
            f"{user} solved level {level} with the answer {answer}",
            0x00FF00,
        ),
    )


def send_admin_action_webhook(text):
    send_webhook(
        BACKEND_WEBHOOK_URL, get_webhook_json("Admin Action", "\n".join(text), 0xFF0000)
    )


def send_acount_creation_webhook(user, name, event):
    send_webhook(
        BACKEND_WEBHOOK_URL,
        {
            "embeds": [
                {
                    "title": "User Registration",
                    "description": f"`{user}` (`{name}`) just registered for the {event} event",
                    "color": 0x00FF00,
                }
            ]
        },
    )


# pylint: enable=E1101
