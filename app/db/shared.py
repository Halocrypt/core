from app.internal.constants import EVENT_NAMES
from app.models.ext import EventModel
from typing import Any
from fastapi.exceptions import HTTPException


def raise_if_invalid_data(*args):
    if any(not x or not ((x).strip() if isinstance(x, str) else True) for x in args):
        raise HTTPException(400, "Invalid Input")


def get_one(q):
    return q.scalars().first()


def get_all(q):
    return q.scalars().all()


def assert_exists(item: Any, name="User"):
    if item is None:
        raise HTTPException(404, f"{name} does not exist")
    return item


def assert_valid_event(event: EventModel):
    if event not in EVENT_NAMES:
        raise HTTPException(404, "Invalid event")
