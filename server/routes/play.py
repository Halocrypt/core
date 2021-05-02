from server.util import api_response, crud
from server.app_init import app
from server.resolvers import play

leaderboard_resolver = play.LeaderboardResolver()
question_resolver = play.QuestionResolver()
answer_resolver = play.AnswerResolver()
event_list_resolver = play.EventListResolver()
get_notification_resolver = play.GetNotificationResolver()


@app.route("/play/<event>/leaderboard/", **crud("get"))
@api_response
def leaderboard(event):
    return leaderboard_resolver.resolve_for(event)


@app.route("/play/<event>/question/", **crud("get"))
@api_response
def question(event):
    return question_resolver.resolve_for(event)


@app.route("/play/<event>/answer/", **crud("post"))
@api_response
def answer(event):
    return answer_resolver.resolve_for(event)


@app.route("/play/<event>/notifications/", **crud("get"))
@api_response
def get_notifications(event):
    return get_notification_resolver.resolve_for(event)


@app.route("/play/events/", **crud("get"))
@api_response
def list_events():
    return event_list_resolver.resolve_for()
