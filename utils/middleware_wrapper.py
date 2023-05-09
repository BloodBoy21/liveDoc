from fastapi import Request
from functools import wraps


def create_middleware_wrapper(**kwargs):
    """
    Create a middleware wrapper for a given function.
    """
    callback = kwargs.get("callback", lambda x: x)

    def wrap_func(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            res = await callback(*args, **kwargs)
            if isinstance(res, dict):
                for key, value in res.items():
                    kwargs[key] = value
            return await func(*args, **kwargs)

        return wrapper

    return wrap_func
