from flask import request
from server.util import AppException


class BaseResolver:
    def resolve_for(self, *args, **kwargs):
        method = request.method.lower()

        resolver = getattr(self, method.lower(), None)
        if resolver is None:
            raise AppException("Unsupported method")
        return resolver(*args, **kwargs)
