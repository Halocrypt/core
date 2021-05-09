from set_env import setup_env

setup_env()
from server.app import app

if __name__ == "__main__":

    app.run(debug=True, port=5000)
