from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse


async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
