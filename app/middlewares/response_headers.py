from fastapi import Request
from time import time

from starlette.responses import PlainTextResponse

EXPOSE_HEADERS = ", ".join(("x-access-token", "x-refresh-token", "x-dynamic"))
ALLOWED_METHODS = "GET, POST, PATCH, PUT, OPTIONS, DELETE"


async def response_header(request: Request, call_next):
    start_time = time()
    if request.method.lower() == "options":
        resp = PlainTextResponse("", 204, headers={"Allow": ALLOWED_METHODS})
    else:
        resp = await call_next(request)
    process_time = round(time() - start_time, 2)
    resp.headers["x-process-time"] = str(process_time)
    resp.headers["access-control-allow-origin"] = request.headers.get("origin", "*")
    resp.headers["access-control-allow-headers"] = request.headers.get(
        "access-control-request-headers", "*"
    )
    resp.headers["access-control-allow-credentials"] = "true"
    resp.headers["x-dynamic"] = "true"
    resp.headers["access-control-max-age"] = "86400"
    resp.headers["access-control-expose-headers"] = EXPOSE_HEADERS
    resp.headers["access-control-allow-methods"] = ALLOWED_METHODS

    return resp