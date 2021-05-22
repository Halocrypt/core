from os import environ as _environ, path
from pathlib import Path
from tempfile import gettempdir

IS_PROD = _environ.get("IS_PROD") is not None

if not IS_PROD:
    print(
        "assuming development environment, add `IS_PROD` to your environment to use the production mode"
    )

# JWT Signing key, make sure this stays same or every user will need to relogin
SIGNING_KEY = _environ["JWT_SIGNING_KEY"]
# How long an access_token will last
TOKEN_EXPIRATION_TIME_IN_SECONDS = 60 * int(_environ.get("TOKEN_EXPIRATION_TIME", 10))

FLASK_SECRET = _environ["FLASK_SECRET"]
DATABASE_URL = (_environ.get("DATABASE_URL") or _environ["DB_URL"]).replace(
    "postgres://", "postgresql+asyncpg://", 1
)
print("[DB]", DATABASE_URL)
REFRESH_TOKEN_SALT = _environ["REFRESH_TOKEN_SALT"]
BACKEND_WEBHOOK_URL = _environ["BACKEND_WEBHOOK_URL"]

MAIL_USER = _environ["MAIL_USER"]
MAIL_PASS = _environ["MAIL_PASS"]

REMOTE_LOG_DB_KEY = _environ["REMOTE_LOG_DB_KEY"]
LOG_SERVER_ENDPOINT = _environ["LOG_SERVER_ENDPOINT"]
BUGSNAG_API_KEY = _environ["BUGSNAG_API_KEY"]
DEALER_KEY = _environ["DEALER_KEY"]
DISABLE_CACHING = _environ.get(
    "DISABLE_CACHING"
)  # dont change unless you know what you're doing

FG_REQUEST_COUNT = int(_environ.get("FG_REQUEST_COUNT", 6))
FG_PER = int(_environ.get("FG_PER", 2))
MIN_QUESTION_TO_LOG = int(_environ.get("MIN_QUESTION_TO_LOG", 5))
try:
    CACHE_DIR = Path(gettempdir(), "@cache").resolve()
    CACHE_DIR.mkdir(exist_ok=True)
except:
    CACHE_DIR = Path(path.dirname(path.realpath(__file__)), "@cache").resolve()
    CACHE_DIR.mkdir(exist_ok=True)
CACHE_DIR = str(CACHE_DIR)
print(f"[Cache] dir: {CACHE_DIR}")

STATIC_DIR = Path(path.dirname(path.realpath(__file__)), "..", "static")
EVENT_NAMES = ("intra", "main")
EDITABLE_FIELDS = ("email", "institution", "name")
del path
del Path
del _environ
del gettempdir