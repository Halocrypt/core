from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.exceptions.base_error import base_error_handler
from app.exceptions.http_error import http_exception_handler
from app.exceptions.validation_error import validation_exception_handler
from app.internal.constants import BUGSNAG_API_KEY, IS_PROD
from app.internal.util import static_file
from app.middlewares.api_guard import api_guard
from app.middlewares.rate_limit_middleware import rate_limit_middleware
from app.middlewares.response_headers import response_header
from app.routers import admin, play, user

app = FastAPI(debug=not IS_PROD)
if IS_PROD:
    print("[BugHandling] Enabled Bugsnag")
    import bugsnag
    from bugsnag.asgi import BugsnagMiddleware

    bugsnag.configure(api_key=BUGSNAG_API_KEY)
    app = BugsnagMiddleware(app)


app.add_exception_handler(Exception, base_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(response_header)
app.middleware("http")(api_guard)


app.include_router(user.router)
app.include_router(play.router)
app.include_router(admin.router)


@app.get("/favicon.ico")
async def favicon():
    return static_file("favicon.ico")


@app.get("/robots.txt")
async def robots():
    return static_file("robots.txt")


@app.get("/o{k}")
async def ok(k: int):
    return {"data": k}
