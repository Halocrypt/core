from set_env import setup_env

setup_env()

from app_init import app

try:
    import routes.user
except ImportError:
    from routes import user


if __name__ == "__main__":
    app.run(debug=True)
