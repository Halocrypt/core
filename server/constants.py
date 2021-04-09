from os import environ as _environ, path
from pathlib import Path
from server.set_env import setup_env as _setup_env

_setup_env()


IS_PROD = _environ.get("IS_DEV") is None

if not IS_PROD:
    print(
        "assuming development environment, remove `IS_DEV` from your environment to use the production mode"
    )

# JWT Signing key, make sure this stays same or every user will need to relogin
SIGNING_KEY = _environ.get("JWT_SIGNING_KEY")
# How long an access_token will last
TOKEN_EXPIRATION_TIME_IN_SECONDS = 60 * int(_environ.get("TOKEN_EXPIRATION_TIME", 10))

FLASK_SECRET = _environ.get("FLASK_SECRET")
DATABASE_URL = _environ.get("DATABASE_URL")
REFRESH_TOKEN_SALT = _environ.get("REFRESH_TOKEN_SALT")

CACHE_DIR = str(Path(path.dirname(path.realpath(__file__)), "@cache").resolve())

del path
del Path
del _environ
