from app.internal.constants import DEALER_KEY, IS_PROD
from fastapi import Request
from fastapi.responses import PlainTextResponse


async def api_guard(request: Request, call_next):
    if IS_PROD and request.headers.get("x-access-key") != DEALER_KEY:
        return PlainTextResponse("No.", 403)

    resp = await call_next(request)

    return resp