from flask import Flask, request

from floodgate import guard
from .constants import DATABASE_URL, FLASK_SECRET, IS_PROD

from .util import (
    get_origin,
    json_response,
)


from server.models import db

app = Flask(__name__)

app.secret_key = FLASK_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.before_request
@guard(ban_time=5, ip_resolver="heroku" if IS_PROD else None, request_count=50, per=15)
def gate_check():
    pass


@app.errorhandler(404)
def catch_all(e):
    return json_response({"error": "not found"})


@app.errorhandler(405)
def method_not_allowed(e):
    return json_response({"error": "Method not allowed"})


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
    return resp
