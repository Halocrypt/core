from http import HTTPStatus
from typing import List
from sqlalchemy import func as _func

from server.models import UserTable as _U, Question as _Q
from server.models import db as _db
from server.util import AppException as _AppException
from server.util import sanitize

lower = _func.lower
count = _func.count


# pylint: disable=E1101
def add_to_db(data, batch=False):
    _db.session.add(data)
    not batch and save_to_db()


# def query_all(table):
#     return table.query.all()


def save_to_db():
    _db.session.commit()


def delete_from_db(d, batch=False):
    if d:
        _db.session.delete(d)
        not batch and save_to_db()


def get_user_by_id(idx: str) -> _U:
    if not idx or sanitize(idx) != idx:
        return _assert_exists(None)
    return _assert_exists(_U.query.filter(lower(_U.user) == lower(idx)).first())


def get_question_by_id(event: str, number: int) -> _Q:
    if number < 0:
        return _assert_exists(None, "Question")
    q = _assert_exists(_Q.query.filter_by(_id=f"{event}:{number}").first())
    return q


def get_latest_q_level(event: str) -> int:
    _assert_exists(event or None, "Event")
    t = _func.max(_Q.question_number)
    curr = _db.session.query(t).filter_by(event=event).first()[0]
    return curr


def get_next_q_level(event: str) -> int:
    t = get_latest_q_level(event)
    return t + 1 if t is not None else 0


def get_questions(event: str) -> List[_Q]:
    return _Q.query.filter_by(event=event).all()


def _assert_exists(user: _U, name="User"):
    if user is None:
        raise _AppException(f"{name} does not exist", HTTPStatus.NOT_FOUND)
    return user


# pylint: enable=E1101
