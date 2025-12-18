from functools import wraps


def _wrap_view_func_with_access(f):
    if hasattr(f, "_wrapped_access"):
        raise
        return f

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self._allow_view_fn(f, *args, **kwargs):
            return self._inaccessible_callback(f, **kwargs)
        return f(self, *args, **kwargs)

    wrapper._wrapped_access = True
    return wrapper


class ViewMeta(type):
    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if callable(value) and not key.startswith("__") and hasattr(value, "_urls"):
                attrs[key] = _wrap_view_func_with_access(value)
        return super().__new__(cls, name, bases, attrs)
