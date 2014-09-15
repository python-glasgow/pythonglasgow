from functools import wraps
from flask import request
from ug import app


def cached(timeout=5 * 60, key='view/%s?%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % (request.path, request.query_string)
            rv = app.cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            app.cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator
