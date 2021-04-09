from set_env import setup_env

setup_env()

from app_init import app


try:
    import routes.user
except ImportError:
    from routes import user


@app.route("/")
def test():
    import requests

    return requests.get("http://localhost:5001/log/x").text


if __name__ == "__main__":
    app.run(debug=True)
