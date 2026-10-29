Authentication and Flask-Login
==============================

Flask-Exts uses Flask-Login to manage authenticated users. Its login extension
registers a ``LoginManager`` and sets ``user.login`` as the login view. For
methods exposed by a Flask-Exts :class:`~flask_exts.admin.View`, use the
``login_required`` decorator exported by ``flask_exts.admin``:

.. code-block:: python

   from flask_exts.admin import View, expose_url, login_required

   class AccountView(View):
       @login_required
       @expose_url("/account/")
       def account(self):
           return "Account"

The Flask-Exts ``View`` metaclass wraps each exposed method with its own access
check. Without an explicit login marker, ``view.allow`` can reject an anonymous
request before Flask-Login's ``login_required`` wrapper runs. That may return
the view's forbidden response instead of redirecting the user to the login
page.

The ``flask_exts.admin.login_required`` decorator applies Flask-Login's
``login_required`` and marks the method for the ``View`` wrapper. For an
anonymous request, the wrapper invokes Flask-Login first, so the request is
redirected to the configured login view (or receives the configured
unauthorized response). For an authenticated request, the normal
``view.allow`` check still runs; requiring a login does not grant permission
to a user who fails the view's authorization rules.

Use Flask-Login's own decorator directly for ordinary Flask routes that are not
methods exposed through a Flask-Exts ``View``. For exposed view methods, import
the decorator from ``flask_exts.admin`` so Flask-Exts can recognize the
requirement:

.. code-block:: python

   # For a Flask-Exts View method:
   from flask_exts.admin import login_required

   # For a regular Flask route, use Flask-Login directly:
   from flask_login import login_required

Active-account checks
---------------------

Authentication and account activity are separate checks. Flask-Login
determines whether a user is authenticated; ``requires_active`` ensures an
authenticated but disabled account cannot use a protected feature. This is
useful for views with ``allow_access = True`` for public endpoints such as
login or registration:

.. code-block:: python

   from flask_exts.admin import (
       View,
       expose_url,
       login_required,
       requires_active,
   )

   class AccountView(View):
       allow_access = True

       @login_required
       @requires_active
       @expose_url("/settings/")
       def settings(self):
           return "Account settings"

Keep this decorator order. The login check handles anonymous users first;
once the user is authenticated, Flask-Exts authorization checks that the
account is active. Methods that must remain reachable by inactive users (for
example, a page used to resend an account verification email) should use
``login_required`` without ``requires_active``.

See :doc:`modelview` for authorization of model views.
