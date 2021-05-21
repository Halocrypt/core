from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    body = ", ".join(f"{x['loc'][-1]}:{x['msg']}" for x in errors)
    return JSONResponse({"error": body}, status_code=400)
