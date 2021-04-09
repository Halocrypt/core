from server.set_env import setup_env

setup_env()
from server.app_init import app
from server.routes import user


if __name__ == "__main__":
    app.run(debug=True)
