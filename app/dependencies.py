from app.models.ext import UserSession
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from app.internal.danger import decode_token
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.db.models import async_session


async def inject_db() -> AsyncSession:
    async with async_session() as session:
        yield session


oauth_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token", auto_error=False)

NULL_USER = UserSession(user=None, is_admin=False)


def _auth(authorization: str, strict: bool):
    if not authorization:
        if strict:
            raise HTTPException(401, "No authentication provided")
        return NULL_USER
    try:
        access_token = decode_token(authorization)
    except Exception:
        if strict:
            raise HTTPException(403, "Invalid token")
        return NULL_USER

    if access_token is None:
        raise HTTPException(200, "refresh")

    return UserSession(**access_token)


def require_auth(token: str = Depends(oauth_scheme)):
    return _auth(token, True)


def require_lax(token: str = Depends(oauth_scheme)):
    return _auth(token, False)


def require_admin(token: str = Depends(oauth_scheme)):
    ret = _auth(token, True)
    if not ret.is_admin:
        raise HTTPException(403, "No.")
    return ret


require_auth.lax = require_lax
require_auth.admin = require_admin