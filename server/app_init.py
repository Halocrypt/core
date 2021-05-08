from flask import Flask, request

from floodgate import guard
from .constants import (
    DATABASE_URL,
    DEALER_KEY,
    FG_PER,
    FG_REQUEST_COUNT,
    FLASK_SECRET,
    IS_PROD,
)

from .util import (
    AppException,
    get_origin,
    json_response,
)


from server.models import db

app = Flask(__name__)


app.secret_key = FLASK_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def resolver(req):
    headers = req.headers
    cf = headers.get("x-real-ip") or headers.get("cf-connecting-ip")
    if cf:
        return cf
    return headers.get("x-forwarded-for", req.remote_addr).split(",")[-1].strip()


@app.before_request
@guard(
    ban_time=5,
    ip_resolver=resolver if IS_PROD else None,
    request_count=FG_REQUEST_COUNT,
    per=FG_PER,
)
def gate_check():
    if request.headers.get("x-access-key") != DEALER_KEY:
        return "no", 403


@app.errorhandler(404)
def catch_all(_):
    return json_response({"error": "not found"}, 400)


@app.errorhandler(405)
def method_not_allowed(_):
    return json_response({"error": "Method not allowed"}, 405)


EXPOSE_HEADERS = ", ".join(("x-access-token", "x-refresh-token", "x-dynamic"))


@app.after_request
def cors(resp):
    origin = get_origin(request.headers)
    resp.headers["access-control-allow-origin"] = origin
    resp.headers["access-control-allow-headers"] = request.headers.get(
        "access-control-request-headers", "*"
    )
    resp.headers["access-control-allow-credentials"] = "true"
    resp.headers["x-dynamic"] = "true"
    resp.headers["access-control-max-age"] = "86400"
    resp.headers["access-control-expose-headers"] = EXPOSE_HEADERS
    resp.headers[
        "access-control-allow-methods"
    ] = "GET, POST, PATCH, PUT, OPTIONS, DELETE"

    return resp
