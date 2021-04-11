import os

import logserver.handler as handler

from flask import Flask, request

LOGSERVER_KEY = os.environ["LOGSERVER_KEY"]

del os
app = Flask(__name__)


@app.route("/log/<t>", methods=["post"])
def index(t):
    key = request.headers.get("x-logserver-key")
    if key != LOGSERVER_KEY:
        return "", 403
    binary = request.get_data()
    handler.push_log(t, binary)
    return "", 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)
