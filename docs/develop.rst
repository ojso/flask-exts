Develop
=======

This guide explains how to set up the project for development, run the test
suite, lint and format code, build the documentation, refresh front-end assets,
and manage translations with Babel.

Environment setup
-----------------

Flask-Exts requires Python 3.10 or later. Use a repository-local virtual
environment instead of the system Python, and install the project in editable
mode so local changes are picked up immediately:

.. code-block:: console

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ python -m pip install -e '.[dev,test]'

The ``dev`` and ``test`` extras install the linting and testing tools. Re-run
the install command after changes to ``pyproject.toml`` so the environment stays
in sync.

If the environment already exists, activate it with:

.. code-block:: console

    $ . venv/bin/activate

Test
----

See :doc:`testing` for test commands, conventions, integration-test models,
and validation guidance.

Lint and format
---------------

Run ruff for Python linting and formatting, and djlint for templates:

.. code-block:: console

    $ python -m ruff check .
    $ python -m ruff format .
    $ python -m djlint src/flask_exts/templates/layout.html --check

Check only the templates you change. The template tree currently contains
pre-existing formatting issues, so a whole-directory ``--check`` reports files
unrelated to your work.

Docs
----

To build the documentation locally:

.. code-block:: console

    $ python -m pip install -r docs/requirements.txt
    $ make docs-build

The build writes HTML to ``docs/_build/html``. Preview it with:

.. code-block:: console

    $ make docs-serve

``make docs-build`` treats Sphinx warnings as errors. Fix warnings introduced
by your change; pre-existing warnings are tracked separately.

Front-end assets
----------------

Bootstrap and other front-end dependencies are managed with npm and copied into
the package's static directory:

.. code-block:: console

    $ npm install
    $ npm run copy:vendor

Run these commands only when changing files under
``src/flask_exts/static``.

Build package
-------------

Building distributions is independent of the development environment. Install
the packaging tools and build the wheel and source distribution:

.. code-block:: console

    $ python -m pip install -e '.[build]'
    $ python -m build

The wheel and source distribution are written to ``dist/``.

Translations
------------

Use Babel to extract, initialize, update, and compile message catalogs.

.. code-block:: console

    # extract messages from source files and generate a POT file
    # (recreate the POT file if it already exists)
    $ pybabel extract -F babel/babel.cfg -o babel/messages.pot src/

    # create new message catalogs from a POT file
    $ pybabel init -i babel/messages.pot -d src/flask_exts/translations -D messages -l en
    $ pybabel init -i babel/messages.pot -d src/flask_exts/translations -D messages -l zh_CN

    # update existing message catalogs from a POT file
    $ pybabel update -i babel/messages.pot -d src/flask_exts/translations -D messages

    # edit the generated .po files in the translation directories

    # compile message catalogs to MO files
    $ pybabel compile -d src/flask_exts/translations -D messages
