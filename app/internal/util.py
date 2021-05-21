# ==================================================
#                  Utility Functions
# ==================================================

from asyncio import iscoroutinefunction
from re import compile as _compile, IGNORECASE
from time import time

import requests
from app.internal.constants import (
    IS_PROD,
    LOG_SERVER_ENDPOINT,
    MIN_QUESTION_TO_LOG,
    REMOTE_LOG_DB_KEY,
    STATIC_DIR,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError

# maybe only strip whitespace?
_sub = _compile(r"([^\w])").sub
sanitize = lambda x: _sub("", f"{x}").strip().lower()

from email_validator import validate_email


def validate_email_address(add):
    try:
        return validate_email(add).email
    except Exception as e:
        raise HTTPException(422, f"{e}")


def js_time():
    return int(time() * 1000)


def validate_num(x):
    if isinstance(x, (int, float)) or str(x).isdigit():
        return int(x)
    raise HTTPException(422, "Expected number")


def static_file(path):
    return FileResponse(STATIC_DIR / path)


def build_call_func(func, args, kwargs):
    async def call_func():
        return (
            await func(*args, **kwargs)
            if iscoroutinefunction(func)
            else func(*args, **kwargs)
        )

    return call_func


# regex to find the offending column
# there must be a better way - RH
find_error = _compile(
    r"Key\s*\(\"?(?P<key>.*?)\"?\)=\((?P<val>.*?)\)", IGNORECASE
).search


def get_integrity_error_cause(error_message: str):
    try:
        match = find_error(error_message)
        print(error_message)
        if not match:
            return None
        k = match.group("key")
        v = match.group("val")
        return k, v
    except Exception as e:
        print(e)
        return None


def check_integrity_error(e):
    # pylint: disable=E1101
    if isinstance(e, IntegrityError) and e.args:
        args = e.args[0]
        # async error wrapping is terrible
        if args and "UniqueViolationError" in args:
            ret = get_integrity_error_cause(args)
            if ret is None:
                raise HTTPException(400, "User exists")
            k, v = ret
            raise HTTPException(400, f'Another account exists with the {k} "{v}"')
    raise e
    # pylint: enable=E1101


def log_answer(user, question, answer, is_correct):
    if question >= MIN_QUESTION_TO_LOG and IS_PROD:
        requests.post(
            f"{LOG_SERVER_ENDPOINT}/add",
            headers={"x-access-key": REMOTE_LOG_DB_KEY},
            json=[user, question, answer, is_correct, js_time()],
        )