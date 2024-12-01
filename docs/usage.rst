=====
Usage
=====

.. _installation:

Installation
==============

To use Flask-Exts, first install it using pip:

.. code-block:: console

   (.venv) $ pip install flask-exts

Configuration
==============

========================== =====================================================================
``BABEL_ENABLED``          Set to ``False`` to disable babel extension.
                           Default is ``True``.
``BABEL_ACCEPT_LANGUAGES`` Set to ``en;zh`` to bebel's accept languages.
                           Default is ``None``.
``BABEL_DEFAULT_TIMEZONE`` Set to ``Asia/Shanghai`` to babel's default timezone.
                           Default is ``None``.
``JQUERY_JS_URL``          Set to ``jquery js url`` to active ``jquery``.
                           Default is in ``template.static``.
``BOOTSTRAP_CSS_URL``      Set to ``bootstrap css url`` to active ``bootstrap css``.
                           Default is in ``template.static``.
``BOOTSTRAP_JS_URL``       Set to ``bootstrap js url`` to active ``bootstrap js``.
                           Default is in ``template.static``.
``ICON_SPRITE_URL``        Set to ``icon url`` to active ``icon``.
                           Default is in ``template.static``.
``CSRF_ENABLED``           Set to ``True`` to enable form's CSRF .
                           Default is ``False``.
``CSRF_SECRET_KEY``        Random data for generating secure tokens.
                           If this is not set then ``SECRET_KEY`` is used.
``CSRF_FIELD_NAME``        Name of the form field and session key that holds the CSRF token.
                           Default is ``csrf_token``.
``CSRF_TIME_LIMIT``        Max age in seconds for CSRF tokens. 
                           Default is ``1800``. 
``TEMPLATE_ENABLED``       Set to ``False`` to disable templating extension.
                           Default is ``True``.
``TEMPLATE_THEME``         Set to ``theme`` to create custom theme                           
                           Default is ``templating.theme.DefaultTheme()``
``USER_ENABLED``           Set to ``False`` to disable ``User`` support. 
                           Default is ``True``. 
``USER_CENTER``            set to ``user center`` to create custom user_center
                           Default is ``users.user_center.DefaultUserCenter()``
``FLASK_LOGIN_ENABLED``    Set to ``False`` to disable ``Flask-Login``. 
                           Default is ``True``. 
========================== =====================================================================

Examples
===========

``python simple.py`` to run a simple example.

.. literalinclude:: ../examples/simple.py
  :language: python

More examples, please click :doc:`examples`.


