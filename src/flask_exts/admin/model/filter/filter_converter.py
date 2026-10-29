import types


def convert_filter(*args):
    """Decorator for field to filter conversion routine."""

    def decorator(func):
        func._converter_for_filter = [x.lower() for x in args]
        return func

    return decorator


class BaseFilterConverter:
    """Base filter converter."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        converters = {}
        for base in cls.__bases__:
            base_map = getattr(base, "_converters", {})
            converters.update(base_map)
        for method in cls.__dict__.values():
            if callable(method) and hasattr(method, "_converter_for_filter"):
                for type_name in method._converter_for_filter:
                    converters[type_name] = method
        cls._converters = converters

    def get_filters(self, column_type, column, name, **kwargs):
        column_type_name = column_type.__class__.__name__.lower()
        filters = self._converters.get(column_type_name, None)
        if filters:
            return types.MethodType(filters, self)(column_type, column, name, **kwargs)
