from server.api_handlers import admin
from server.app_init import app
from server.util import ParsedRequest, api_response


@app.get("/admin/<event>/users/", strict_slashes=False)
@api_response
def user_list(event):
    return admin.event_users(event)


@app.patch("/admin/accounts/<user>/disqualify/", strict_slashes=False)
@api_response
def disqualify(user):
    return admin.disqualify(ParsedRequest(), user)


@app.patch("/admin/accounts/<user>/requalify/", strict_slashes=False)
@api_response
def requalify(user):
    return admin.requalify(user)


@app.post("/admin/<event>/questions/add/", strict_slashes=False)
@api_response
def add_question(event):
    return admin.add_question(ParsedRequest(), event)


@app.patch("/admin/<event>/questions/<int:number>/", strict_slashes=False)
@api_response
def edit_questions(event, number):
    return admin.edit_question(ParsedRequest(), event, number)


@app.get("/admin/events/<event>/questions/", strict_slashes=False)
@api_response
def list_questions(event):
    return admin.list_questions(event)


@app.patch("/admin/events/<event>/", strict_slashes=False)
@api_response
def edit_event(event):
    return admin.edit_event(ParsedRequest(), event)


@app.get("/admin/yek-revresgol/", strict_slashes=False)
@api_response
def logserver_key():
    return admin.logserver_key()


@app.delete("/admin/<event>/notifications/<int:ts>/", strict_slashes=False)
@api_response
def delete_notification(event, ts):
    return admin.delete_notification(event, ts)


@app.patch("/admin/<event>/notifications/", strict_slashes=False)
@api_response
def add_notification(event):
    return admin.add_notification(ParsedRequest(), event)


@app.get("/admin/<event>/user-count/", strict_slashes=False)
@api_response
def user_count(event):
    return admin.user_count(event)


@app.get("/admin/-/invalidate/", strict_slashes=False)
@api_response
def invalidate_keys():
    return admin.invalidate_listener(ParsedRequest())
