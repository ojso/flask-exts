Develop
=======

This guide explains how to set up the project for development, run the test
suite, lint and format code, build the documentation, refresh front-end assets,
and manage translations with Babel.

Environment setup
-----------------

Flask-Exts requires Python 3.11 or later. The primary development version is
Python 3.13, matching the default in Debian 13 stable; 3.11 remains the minimum
supported version. Development uses `uv
<https://docs.astral.sh/uv/>`_ to manage a repository-local virtual
environment. Install uv, then run:

.. code-block:: console

    $ uv sync

``uv sync`` creates ``.venv``, installs the project in editable mode, and
installs the ``dev`` dependency group. That group includes the linting and
testing tools as well as the Sphinx dependencies used to build the
documentation. Re-run ``uv sync`` after changes to ``pyproject.toml`` so the
environment stays in sync.

If the environment already exists, activate it with:

.. code-block:: console

    $ . .venv/bin/activate

Commands can also be run without activation by prefixing them with ``uv run``,
for example ``uv run pytest``.

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

Building distributions is independent of the development environment. Build the
wheel and source distribution with:

.. code-block:: console

    $ uv build

The wheel and source distribution are written to ``dist/``.

Changelog and versioning
------------------------

User-visible changes are recorded in ``CHANGES.rst``. The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_ and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

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
