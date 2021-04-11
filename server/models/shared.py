from flask_sqlalchemy import SQLAlchemy
from server.util import AppException

db = SQLAlchemy()


def raise_if_invalid_data(*args):
    if any(not x or not ((x).strip() if isinstance(x, str) else True) for x in args):
        raise AppException("Invalid Input")


EVENT_NAMES = ("intra", "main")
