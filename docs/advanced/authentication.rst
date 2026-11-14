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
``request_loader`` also checks ``is_active`` and rejects a token whose ``pwd``
claim no longer matches the user's current password hash.

Protected routes therefore only need ``login_required``; disabled accounts are
already anonymous by the time authorization runs. Views that set
``allow_access = True`` stay public for anonymous users such as login and
registration.

Failed-login lockout
--------------------

``SqlaUserStore`` counts consecutive failed authentication steps on the user
row (``failed_login_count`` and ``locked_until``). Password failures and
second-factor failures share the counter, because both are failed attempts
against the same account. The counter is cleared only after the whole login
flow succeeds, or after a successful password reset.

The account is locked once ``USER_LOGIN_MAX_FAILURES`` is reached. Each further
failure doubles the delay, starting at ``USER_LOGIN_LOCKOUT_BASE_SECONDS`` and
capped at ``USER_LOGIN_LOCKOUT_MAX_SECONDS``. While locked, the login view
reports the remaining time, and a pending second-factor session cannot be
resumed.

Lockout state is separate from ``is_active``: it expires on its own, and an
administrator can clear it with ``user_set(user, failed_login_count=0,
locked_until=None)``. Because the counter lives on the user row, a lockout is
independent of the client IP and shared by every application process using the
same database. This complements, but does not replace, request-rate limiting at
the reverse proxy: a proxy can still reject high-frequency traffic and attempts
against usernames that do not exist.

Custom user stores
------------------

``flask_exts.userstore.base.UserStore`` declares every member that
``UserView`` relies on. A subclass that omits one cannot be instantiated, so a
missing method fails at startup with the Python ABC error instead of later with
``AttributeError`` during login. The login-related members are
``login_user_by_username_password``, ``is_locked``,
``record_login_failure``, and ``clear_login_failures``.

API authentication
------------------

Flask-Login's ``request_loader`` only accepts a Bearer token in the
``Authorization`` header::

   Authorization: Bearer <JWT>

The auth-scheme is case-insensitive, so ``bearer`` and ``Bearer`` are both
accepted. API-key query parameters (``?api_key=...``) and HTTP Basic
authentication are not supported and are not checked.

Issue tokens through
``flask_exts.builtin_extensions.login_ext.jwt_encode_for_user``. The helper
adds ``pwd`` and ``amr`` claims so that the request loader can bind a token to
the user's current credentials:

- ``pwd`` is a keyed fingerprint of the current password hash. Changing or
  resetting the password invalidates every previously issued token. Tokens
  without ``pwd`` are rejected; there is no compatibility mode.
- ``amr`` lists the completed authentication methods. It always contains
  ``pwd``; add ``otp`` only after verifying a TOTP code or recovery code. A
  user with ``tfa_enabled=True`` needs an ``otp`` entry, otherwise the helper
  raises ``ValueError`` and the request loader rejects the token.
- ``iat``, ``exp``, and ``token_use="access"`` are written by
  ``jwt_encode``. ``JWT_ACCESS_TOKEN_MAX_AGE`` controls the lifetime
  (default 900 seconds). ``JWT_LEEWAY`` optionally tolerates clock skew
  between application instances.

``JWT_SECRET_KEY`` must be set before issuing or validating a token, must be at
least 32 bytes, and must differ from ``SECRET_KEY``. ``JWT_HASH`` is restricted
to ``HS256``, ``HS384``, or ``HS512``; any other value, including ``none``,
raises ``RuntimeError`` at first use.

The helper only encodes the claims it is given. It cannot verify a second
factor, so application code must complete TFA verification before passing
``amr="otp"``.

See :doc:`modelview` for authorization of model views.
