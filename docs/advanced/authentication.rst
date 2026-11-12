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

Disabled accounts
-----------------

``is_active`` is an administrative lock, independent of email verification.
Disabled accounts cannot log in: the login view refuses them, and the Flask-Login
``user_loader`` rejects a disabled account's existing session on its next
request, clearing the session id and the remember-me cookie. The JWT
``request_loader`` also checks ``is_active``.

Protected routes therefore only need ``login_required``; disabled accounts are
already anonymous by the time authorization runs. Views that set
``allow_access = True`` stay public for anonymous users such as login and
registration.

API authentication
------------------

Flask-Login's ``request_loader`` only accepts a Bearer token in the
``Authorization`` header::

   Authorization: Bearer <JWT>

API-key query parameters (``?api_key=...``) and HTTP Basic authentication are
not supported and are not checked.

See :doc:`modelview` for authorization of model views.
