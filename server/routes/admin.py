from server.app_init import app
from server.util import POST_REQUEST, ParsedRequest, api_response
from server.api_handlers import admin


@app.route("/admin/<event>/users/", strict_slashes=False)
@api_response
def event_users(event):
    return admin.event_users(event)


@app.route("/admin/accounts/<user>/disqualify/", **POST_REQUEST)
@api_response
def disqualify(user):
    return admin.disqualify(ParsedRequest(), user)


@app.route("/admin/accounts/<user>/requalify/", strict_slashes=False)
@api_response
def requalify(user):
    return admin.requalify(user)


@app.route("/admin/accounts/<user>/delete/", strict_slashes=False)
@api_response
def delete(user):
    return admin.delete(user)


@app.route("/admin/<event>/questions/add/", **POST_REQUEST)
@api_response
def add_question(event):
    return admin.add_question(ParsedRequest(), event)


@app.route("/admin/<event>/questions/<int:number>/edit", **POST_REQUEST)
@api_response
def edit_questions(event, number):
    return admin.edit_question(ParsedRequest(), event, number)


@app.route("/admin/events/<event>/questions/", strict_slashes=False)
@api_response
def list_questions(event):
    return admin.list_questions(event)


@app.route("/admin/events/<event>/edit/", **POST_REQUEST)
@api_response
def edit_event(event):
    return admin.edit_event(ParsedRequest(), event)


@app.route("/admin/events/", strict_slashes=False)
@api_response
def list_events():
    return admin.list_events()


@app.route("/admin/notificaton-key/", strict_slashes=False)
@api_response
def notification_key():
    return admin.notification_key()


@app.route("/admin/yek-revresgol/", strict_slashes=False)
@api_response
def logserver_key():
    return admin.logserver_key()


@app.route("/admin/<event>/user-count/", strict_slashes=False)
@api_response
def user_count(event):
    return admin.user_count(ParsedRequest(), event)