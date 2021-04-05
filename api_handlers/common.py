from sqlalchemy import func as _func

from app_init import UserTable as _U
from app_init import db as _db
from util import AppException as _AppException
from util import sanitize

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


# def delete_from_db(d, batch=False):
#     if d:
#         _db.session.delete(d)
#         not batch and save_to_db()


def get_user_by_id(idx: str) -> _U:
    if not idx or sanitize(idx) != idx:
        return _assert_exists(None)
    return _assert_exists(_U.query.filter(lower(_U.user) == lower(idx)).first())


def _assert_exists(user: _U, name="User"):
    if user is None:
        raise _AppException(f"{name} does not exist")
    return user


# pylint: enable=E1101
