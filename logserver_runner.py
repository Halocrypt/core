from logging import debug
from set_env import setup_env

setup_env()
from logserver.app import app

if __name__ == "__main__":
    from logserver.app import app

    app.run(debug=True, port=5001)
