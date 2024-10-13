from flask import g


def set_current_view(view):
    g._admin_view = view


def get_current_view():
    return getattr(g, "_admin_view", None)


def get_template_args():
    args = getattr(g, "_admin_template_args", None)
    if args is None:
        args = g._admin_template_args = dict()
    return args
