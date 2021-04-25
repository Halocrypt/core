from server.util import api_response, crud
from server.app_init import app
from server.resolvers import play

leaderboard_resolver = play.LeaderboardResolver()
question_resolver = play.QuestionResolver()
answer_resolver = play.AnswerResolver()


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
