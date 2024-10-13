def expose(url="/", methods=("GET",)):
    """
    Use this decorator to expose views in your view classes.

    :param url:
        Relative URL for the view
    :param methods:
        Allowed HTTP methods. By default only GET is allowed.
    """

    def wrap(f):
        if not hasattr(f, "_urls"):
            f._urls = []
        f._urls.append((url, methods))
        return f

    return wrap


def expose_plugview(url="/"):
    """
    Decorator to expose Flask's pluggable view classes
    (``flask.views.View`` or ``flask.views.MethodView``).

    :param url:
        Relative URL for the view
    """

    def wrap(v):
        handler = expose(url, v.methods)

        if hasattr(v, "as_view"):
            return handler(v.as_view(v.__name__))
        else:
            return handler(v)

    return wrap
