from fastapi.responses import JSONResponse


async def base_error_handler(request, exc: Exception):
    return JSONResponse(
        {"error": "An unknown error occured", "tb": f"{exc}"},
        status_code=exc.status_code,
    )
