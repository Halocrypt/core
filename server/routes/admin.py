from server.app_init import app
from server.util import POST_REQUEST, ParsedRequest, api_response
from server.api_handlers import admin


@app.route("/admin/accounts/<user>/disqualify/", **POST_REQUEST)
@api_response
def disqualify(user):
    return admin.disqualify(ParsedRequest(), user)


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


@app.route("/admin/<event>/questions/", strict_slashes=False)
@api_response
def list_questions(event):
    return admin.list_questions(event)
