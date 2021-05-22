from app.internal.util import build_call_func
from functools import wraps
from fastapi import Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from traceback import print_exc


def api_response(func):
    # this has to be done otherwise flask will perceive all view_functions as `run`
    @wraps(func)
    async def run(*args, **kwargs):
        try:
            call = build_call_func(func, args, kwargs)
            ret = await call()
            if isinstance(ret, Response):
                return ret
            return {"data": ret}
        except HTTPException as e:
            return JSONResponse(
                {"error": e.detail}, status_code=int(e.status_code or 200)
            )
        except Exception as e:
            print_exc()
            err = "An unknown error occured"
            return JSONResponse({"error": err, "tb": f"{e}"}, status_code=500)

    return run