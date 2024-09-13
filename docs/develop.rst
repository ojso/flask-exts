=======
Develop
=======

Install
=======

.. code-block:: console

    $ pip install -e .
    $ pip install -r requirements/develop.in

Test
====
Tests are run with `pytest <https://pytest.org/>`_.
To run the tests, from the project directory:

.. code-block:: console

    # requirements
    $ pip install -r requirements/test.in    

    # update translation
    $ pybabel compile -d src/flask_exts/translations -D messages
    $ pybabel compile -d tests/translations
    
    # test
    $ pytest

Docs
====

.. code-block:: console

    $ pip install -r docs/requirements.txt
    $ cd docs
    $ make html

Publish
=======

.. code-block:: console

    $ pip install -r requirements/build.in
    $ python -m build

