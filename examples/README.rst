This page lists the runnable example applications for Flask-Exts and shows how to
run them locally.

Setup
-----

Clone the repository and install the development environment with uv:

.. code-block:: bash

    $ git clone https://github.com/ojso/flask-exts.git
    $ cd flask-exts
    $ uv sync

Run the examples
----------------

After starting an example, open the local admin page in your browser:
``http://localhost:5000``.

simple
^^^^^^

This example creates a minimal page and registers it with the admin interface.

.. code-block:: bash

    $ cd examples/simple
    $ uv run flask --app __init__ run

The app will be available at ``http://localhost:5000``.

demo
^^^^

This example provides a basic demo application with a default admin user.

Default login:

- username: ``admin``
- password: ``admin``

.. code-block:: bash

    $ cd examples/demo
    $ uv run flask --app __init__ run

The app will be available at ``http://localhost:5000``.

