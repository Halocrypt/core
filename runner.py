from server.set_env import setup_env

setup_env()

from logserver.app import app as log_app
from server.app import app as core_app


def run_logserver():
    log_app.run(debug=True, port=5001)


def run_coreserver():
    core_app.run(debug=True, port=5000)


if __name__ == "__main__":
    from sys import argv

    if not len(argv) > 1:
        raise Exception("No argument provided: (either coreserver/logserver)")

    arg = argv[1]
    if arg == "logserver":
        run_logserver()
    elif arg == "coreserver":
        run_coreserver()
    else:
        raise Exception("Invalid option supported: coreserver/logserver")