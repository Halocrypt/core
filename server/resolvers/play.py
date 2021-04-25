from server.resolvers.base_resolver import BaseResolver
from server.api_handlers import play
from server.util import ParsedRequest


class LeaderboardResolver(BaseResolver):
    def get(self, event):
        return play.leaderboard(event)


class QuestionResolver(BaseResolver):
    def get(self, event):
        return play.question(event)


class AnswerResolver(BaseResolver):
    def post(self, event):
        return play.answer(ParsedRequest(), event)
