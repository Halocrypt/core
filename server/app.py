from flask.helpers import send_from_directory
import bugsnag
from bugsnag.flask import handle_exceptions
from server.app_init import app
from server.routes import user, admin, play
from server.constants import BUGSNAG_API_KEY, IS_PROD


#if IS_PROD:
#   bugsnag.configure(api_key=BUGSNAG_API_KEY)
#   handle_exceptions(app)


def serve_static_file(file: str):
    ONE_YEAR_IN_SECONDS = 60 * 60 * 24 * 365
    # we disallow all bots here because we don't want useless crawling over the API
    return send_from_directory("static", file, cache_timeout=ONE_YEAR_IN_SECONDS)


@app.route("/robots.txt")
def robots():
    return serve_static_file("robots.txt")


@app.route("/favicon.ico")
def favicon():
    return serve_static_file("favicon.ico")


if __name__ == "__main__":
    app.run(debug=True)
