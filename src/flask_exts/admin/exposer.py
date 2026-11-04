from flask_login import login_required as flask_login_required


def expose_url(url="/", methods=("GET",)):
    """Use this decorator to expose views in your view classes.

    Args:
        url:
            Relative URL for the view
        methods:
            Allowed HTTP methods. By default only GET is allowed.
    """

    def wrap(f):
        if not hasattr(f, "_urls"):
            f._urls = []
        f._urls.append((url, methods))
        return f

    return wrap


def login_required(f):
    """Apply Flask-Login and mark the view for login-first dispatch."""
    f = flask_login_required(f)
    f._login_required = True
    return f


def requires_active(f):
    """Mark a view method as requiring an active account.

    ``View.allow_access = True`` lets a whole view class bypass the
    authorizer's ``is_active`` check (it's meant for genuinely public
    endpoints like login/register). Methods on such a class that are
    account-authenticated features -- change password, profile, enabling
    TFA, etc. -- should be marked with this decorator so a disabled
    (``is_active=False``) account's existing session cannot still use them.

    Stack this above ``@expose_url`` and below ``@login_required``, e.g.::

        @login_required
        @requires_active
        @expose_url("/profile/")
        def profile(self):
            ...
    """
    f._requires_active = True
    return f


def expose_action(name, text, confirmation=None):
    """Use this decorator to expose actions that span more than one entity (model,

    file, etc)

    Args:
        name:
            Action name
        text:
            Action text.
        confirmation:
            Confirmation text. If not provided, action will be executed
            unconditionally.
    """

    def wrap(f):
        f._action = (name, text, confirmation)
        return f

    return wrap
