==========
Configure
==========

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。

English summary: This page lists the most commonly used Flask-Exts configuration options for admin access, CSRF, i18n, and email behavior.
中文说明：本页列出 Flask-Exts 常用配置项，涵盖后台访问控制、CSRF、国际化和邮件设置等关键功能。

========================== ============================================================================
``ADMIN_ALLOW_ACCESS``     Set to ``False`` to limit admin view access to role‑granted users only;
                           otherwise, all users have access.
                           Default is ``True``.
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
                           Default is ``None``.
========================== ============================================================================
