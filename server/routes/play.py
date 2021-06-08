from flask import send_from_directory
from server.api_handlers import play
from server.app_init import app

from server.util import ParsedRequest, api_response


@app.get("/play/<event>/leaderboard/", strict_slashes=False)
@api_response
def leaderboard(event):
    return play.leaderboard(event)


# @app.get("/play/main/leaderboard/", strict_slashes=False)
# def leaderboard():
#    return send_from_directory("static", "leaderboard.json")


@app.get("/play/<event>/question/", strict_slashes=False)
@api_response
def question(event):
    return play.question(event)


@app.post("/play/<event>/answer/", strict_slashes=False)
@api_response
def answer(event):
    return play.answer(ParsedRequest(), event)


@app.get("/play/<event>/notifications/", strict_slashes=False)
@api_response
def get_notifications(event):
    return play.get_notifications(event)


@app.get("/play/events/", strict_slashes=False)
@api_response
def list_events():
    return play.list_events()
