# ==================================================
#                  Utility Functions
# ==================================================
from email.utils import parseaddr as _parseaddr
from functools import wraps as _wraps
from http import HTTPStatus
from json import dumps as _dumps
from re import compile as _compile
from time import time
from traceback import print_exc as _print_exc


from flask import Response as _Response
from flask import request as _request
from werkzeug.datastructures import Headers

# maybe only strip whitespace?
_sub = _compile(r"([^\w])").sub
sanitize = lambda x: _sub("", x).strip().lower()


def validate_email_address(email_id: str) -> str:
    if "@" in _parseaddr(email_id)[1]:
        return email_id
    raise AppException("Invalid Email", HTTPStatus.BAD_REQUEST)


def get_origin(headers: Headers, or_="*") -> str:
    """
    for CORS requests
    On client we will send the x-qbytic-origin header
    or a query string to specify the origin

    Args:
        request (_Request): Flask request object

    Returns:
        str: the origin value
    """
    get = headers.get
    return get("Origin") or or_


class ParsedRequest:
    def __init__(self):
        self.args = dict(_request.args)
        self.headers = _request.headers
        self.json: dict = _request.get_json() or {}
        self.method = _request.method


def json_response(data: dict, status=200, headers=None) -> _Response:
    dump = _dumps(data)
    resp = _Response(
        dump, status=status, headers=headers, content_type="application/json"
    )
    return resp


def api_response(func):
    # this has to be done otherwise flask will perceive all view_functions as `run`
    @_wraps(func)
    def run(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            if isinstance(ret, _Response):
                return ret
            return json_response({"data": ret})

        except AppException as e:

            return json_response({"error": e.message}, status=int(e.code or 200))
        except Exception as e:
            _print_exc()
            err = "An unknown error occured"
            return json_response({"error": err, "tb": f"{e}"})

    return run


def js_time():
    return int(time() * 1000)


def get_bearer_token(headers: Headers) -> str:
    auth = headers.get("Authorization", "")
    # count= 1 as in the rare case that the bearer token itself has the word Bearer in it we want it intact
    return auth.replace("Bearer", "", 1).strip()


def validate_num(x):
    if isinstance(x, int) or str(x).isdigit():
        return int(x)
    raise AppException("Expected number")


# A special error class which is caught by our request handler
# if you throw this error anywhere during a request execution,
# we will send the error message in a json respose
class AppException(Exception):
    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message


def crud(*methods):
    return {"strict_slashes": False, "methods": methods}
