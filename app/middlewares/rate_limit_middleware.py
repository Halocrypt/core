from app.internal.constants import FG_PER, FG_REQUEST_COUNT
from app.internal.util import ip_resolver
from floodgate.fastapi import guard

rate_limit_middleware = guard(
    ban_time=5,
    ip_resolver=ip_resolver,
    request_count=FG_REQUEST_COUNT,
    per=FG_PER,
)
