def expose_url(url="/", methods=("GET",)):
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


def expose_action(name, text, confirmation=None):
    """
    Use this decorator to expose actions that span more than one entity (model, file, etc)

    :param name:
        Action name
    :param text:
        Action text.
    :param confirmation:
        Confirmation text. If not provided, action will be executed unconditionally.
    """

    def wrap(f):
        f._action = (name, text, confirmation)
        return f

    return wrap
