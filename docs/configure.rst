==========
Configure
==========

Configuration
==============

========================== =====================================================================
``ADMIN_ALL_ACCESSED``     Set to ``True`` to enable access within admin views for all users,
                           otherwise, only the users with access role can access admin views.
                           Default is ``False``.
``BABEL_ACCEPT_LANGUAGES`` Set to ``en;zh`` to bebel's accept languages.
                           Default is ``None``.
``BABEL_DEFAULT_TIMEZONE`` Set to ``Asia/Shanghai`` to babel's default timezone.
                           Default is ``None``.
``CSRF_ENABLED``           Set to ``False`` to enable form's CSRF .
                           Default is ``True``.
``CSRF_SECRET_KEY``        Random data for generating secure tokens.
                           If this is not set then ``SECRET_KEY`` is used.
``CSRF_FIELD_NAME``        Name of the form field and session key that holds the CSRF token.
                           Default is ``csrf_token``.
``CSRF_TIME_LIMIT``        Max age in seconds for CSRF tokens. 
                           Default is ``1800``. 
``NOREPLY_EMAIL_SENDER``   Email address used to send emails.
                           It is a dict for smtp with keys: host,port,user,password.
                           Default is None.
========================== =====================================================================

