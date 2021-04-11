from server.util import POST_REQUEST, ParsedRequest, api_response
from server.app_init import app
from server.api_handlers import play


@app.route("/play/<event>/leaderboard/", strict_slashes=False)
@api_response
def leaderboard(event):
    return play.leaderboard(event)


@app.route("/play/<event>/question/", strict_slashes=False)
@api_response
def question(event):
    return play.question(event)


@app.route("/play/<event>/answer/", **POST_REQUEST)
@api_response
def answer(event):
    return play.answer(ParsedRequest(), event)


@app.route("/play/<event>/user-count/", strict_slashes=False)
@api_response
def user_count(event):
    return play.user_count(ParsedRequest(), event)