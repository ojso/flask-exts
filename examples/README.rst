========================
Examples
========================

Install
=========

Type these commands in the terminal:

.. code-block:: bash

    $ git clone https://github.com/ojso/flask-exts.git
    $ cd flask-exts/examples
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install flask-exts
    

Run the demo applications
==========================

Type the command in the terminal:

.. code-block:: bash

    $ flask --app start run --debug --port=5000

Bootstrap 4
-----------------

If not set `app.config["ICON_SPRITE_URL"]`, please link `icons/bootstrap-icons.svg` to `bootstrap4/static/icons/bootstrap-icons.svg`.

.. code-block:: bash

    $ mkdir bootstrap4/static/icons
    $ ln -s ../../../icons/bootstrap-icons.svg  bootstrap4/static/icons/bootstrap-icons.svg
    $ flask --app bootstrap4/app.py run

Bootstrap 5
-----------------

If not set `app.config["ICON_SPRITE_URL"]`, please link `icons/bootstrap-icons.svg` to `bootstrap5/static/icons/bootstrap-icons.svg`.

.. code-block:: bash
    
    $ mkdir bootstrap5/static/icons
    $ ln -s ../../../icons/bootstrap-icons.svg  bootstrap5/static/icons/bootstrap-icons.svg
    $ flask --app bootstrap5/app.py run

Now go to http://localhost:5000.


Overview of icons
-----------------

When Bootstrap-Flask updates the icon file, the overview page can be upgraded with:


.. code-block:: bash

    $ python3 update-icons.py

