from server.resolvers.base_resolver import BaseResolver
from server.api_handlers import admin
from server.util import ParsedRequest


class UserListResolver(BaseResolver):
    def get(self, event):
        return admin.event_users(event)


class DisqualificationResolver(BaseResolver):
    def patch(self, username):
        return admin.disqualify(ParsedRequest(), username)


class RequalificationResolver(BaseResolver):
    def patch(self, username):
        return admin.requalify(username)


class AddQuestionResolver(BaseResolver):
    def post(self, event):
        return admin.add_question(ParsedRequest(), event)


class EditQuestionResolver(BaseResolver):
    def patch(self, event, number):
        return admin.edit_question(ParsedRequest(), event, number)


class QuestionListResolver(BaseResolver):
    def get(self, event):
        return admin.list_questions(event)


class EventEditResolver(BaseResolver):
    def patch(self, event):
        return admin.edit_event(ParsedRequest(), event)


class EventListResolver(BaseResolver):
    def get(self):
        return admin.list_events()


class NotificationKeyResolver(BaseResolver):
    def get(self):
        return admin.notification_key()


class LogserverKeyResolver(BaseResolver):
    def get(self):
        return admin.logserver_key()


class UserCountResolver(BaseResolver):
    def get(self, event):
        return admin.user_count(event)