from server.resolvers import admin
from server.app_init import app
from server.util import api_response, crud

user_list_resolver = admin.UserListResolver()
disqualification_resolver = admin.DisqualificationResolver()
requalification_resolver = admin.RequalificationResolver()
add_question_resolver = admin.AddQuestionResolver()
edit_question_resolver = admin.EditQuestionResolver()
question_list_resolver = admin.QuestionListResolver()
event_edit_resolver = admin.EventEditResolver()
notification_key_resolver = admin.NotificationKeyResolver()
logserver_key_resolver = admin.LogserverKeyResolver()
user_count_resolver = admin.UserCountResolver()


@app.route("/admin/<event>/users/", **crud("get"))
@api_response
def user_list(event):
    return user_list_resolver.resolve_for(event)


@app.route("/admin/accounts/<user>/disqualify/", **crud("patch"))
@api_response
def disqualify(user):
    return disqualification_resolver.resolve_for(user)


@app.route("/admin/accounts/<user>/requalify/", **crud("patch"))
@api_response
def requalify(user):
    return requalification_resolver.resolve_for(user)


@app.route("/admin/<event>/questions/add/", **crud("post"))
@api_response
def add_question(event):
    return add_question_resolver.resolve_for(event)


@app.route("/admin/<event>/questions/<int:number>/", **crud("patch"))
@api_response
def edit_questions(event, number):
    return edit_question_resolver.resolve_for(event, number)


@app.route("/admin/events/<event>/questions/", **crud("get"))
@api_response
def list_questions(event):
    return question_list_resolver.resolve_for(event)


@app.route("/admin/events/<event>/", **crud("patch"))
@api_response
def edit_event(event):
    return event_edit_resolver.resolve_for(event)


@app.route("/admin/notificaton-key/", **crud("get"))
@api_response
def notification_key():
    return notification_key_resolver.resolve_for()


@app.route("/admin/yek-revresgol/", **crud("get"))
@api_response
def logserver_key():
    return logserver_key_resolver.resolve_for()


@app.route("/admin/<event>/user-count/", **crud("get"))
@api_response
def user_count(event):
    return user_count_resolver.resolve_for(event)
