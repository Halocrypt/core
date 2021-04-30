from os import environ as _environ, path
from pathlib import Path


IS_PROD = _environ.get("IS_DEV") is None

if not IS_PROD:
    print(
        "assuming development environment, remove `IS_DEV` from your environment to use the production mode"
    )

# JWT Signing key, make sure this stays same or every user will need to relogin
SIGNING_KEY = _environ["JWT_SIGNING_KEY"]
# How long an access_token will last
TOKEN_EXPIRATION_TIME_IN_SECONDS = 60 * int(_environ.get("TOKEN_EXPIRATION_TIME", 10))

FLASK_SECRET = _environ["FLASK_SECRET"]
DATABASE_URL = _environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)

REFRESH_TOKEN_SALT = _environ["REFRESH_TOKEN_SALT"]
BACKEND_WEBHOOK_URL = _environ["BACKEND_WEBHOOK_URL"]

MAIL_USER = _environ["MAIL_USER"]
MAIL_PASS = _environ["MAIL_PASS"]
NOTIFICATION_KEY = _environ["NOTIFICATION_KEY"]
REMOTE_LOG_DB_KEY = _environ["REMOTE_LOG_DB_KEY"]
LOGSERVER_KEY = _environ["LOGSERVER_KEY"]
DISABLE_CACHING = _environ.get(
    "DISABLE_CACHING"
)  # dont change unless you know what you're doing

FG_REQUEST_COUNT = int(_environ.get("FG_REQUEST_COUNT", 6))
FG_PER = int(_environ.get("FG_PER", 2))
MIN_QUESTION_TO_LOG = int(_environ.get("MIN_QUESTION_TO_LOG", 5))
CACHE_DIR = str(Path(path.dirname(path.realpath(__file__)), "@cache").resolve())
EVENT_NAMES = ("intra", "main", "dev")

del path
del Path
del _environ
