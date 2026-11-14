Configure
==========

This page lists the most commonly used Flask-Exts configuration options for
admin access, CSRF, i18n, and email behavior.

.. list-table:: Common configuration options
   :header-rows: 1
   :widths: 28 72

   * - Name
     - Description
   * - ``APP_NAME``
     - Application name used as the issuer in TOTP provisioning URIs.
       Default is ``"UnknownApp"``.
   * - ``BABEL_ACCEPT_LANGUAGES``
     - Set to ``en;zh`` for Babel's accepted languages.
       Default is ``None``.
   * - ``BABEL_DEFAULT_TIMEZONE``
     - Set to ``Asia/Shanghai`` as the default timezone for Babel.
       Default is ``None``.
   * - ``CSRF_ENABLED``
     - Set to ``False`` to disable CSRF protection for forms.
       Default is ``True``.
   * - ``CSRF_SECRET_KEY``
     - Random data used to generate secure tokens.
       If not set, a CSRF-specific key is derived from ``SECRET_KEY``.
   * - ``CSRF_FIELD_NAME``
     - Name of the form field and session key that stores the CSRF token.
       Default is ``csrf_token``.
   * - ``CSRF_TIME_LIMIT``
     - Maximum age of a CSRF token in seconds.
       Default is ``1800``.
   * - ``SECRET_KEY``
     - Flask's master secret. Flask-Exts derives separate keys from it for
       CSRF tokens, URL tokens, and BLAKE2b fingerprints. Deploying this
       key-separation change invalidates existing CSRF/URL tokens and active
       login sessions; changing ``SECRET_KEY`` also invalidates Flask sessions.
   * - ``NOREPLY_EMAIL_SENDER``
     - Email address used to send notifications.
       This is a dict for SMTP configuration with keys such as
       ``host``, ``port``, ``user``, and ``password``.
       TLS certificate and hostname verification are enabled and use the
       default CA store; configure a private CA through ``SSL_CERT_FILE`` or
       the system trust store instead of disabling verification.
       Default is ``None``.
   * - ``USER_LOGIN_MAX_FAILURES``
     - Consecutive failed authentication steps allowed before the account is
       locked. Password and second-factor failures share the counter.
       Default is ``5``.
   * - ``USER_LOGIN_LOCKOUT_BASE_SECONDS``
     - First lockout duration in seconds. Each further failure doubles it.
       Default is ``60``.
   * - ``USER_LOGIN_LOCKOUT_MAX_SECONDS``
     - Upper bound for the lockout duration in seconds.
       Default is ``3600``.

For more advanced behavior, see :doc:`advanced/index` and :doc:`examples`.
