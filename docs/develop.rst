Develop
=======

This guide explains how to install the project for development, run the test
suite, build the documentation, and manage translations with Babel.

Install
-------

Install the project in editable mode so local changes are picked up immediately:

.. code-block:: console

    $ pip install -e .

Test
----

The project uses `pytest <https://pytest.org/>`_ for testing. From the project
root, run:

.. code-block:: console

    # install test dependencies
    $ pip install -r requirements/test.in

    # run the test suite
    $ pytest

Docs
----

To build the documentation locally:

.. code-block:: console

    $ pip install -r docs/requirements.txt
    $ cd docs
    $ make html

Develop
-------


.. code-block:: console

    # develop with jinja formatter, and so on.
    $ pip install -r requirements/develop.in

Build package
-------------

To build a distributable package:

.. code-block:: console

    $ pip install -r requirements/build.in
    $ python -m build

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
