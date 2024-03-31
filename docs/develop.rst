Develop
=======

Install
-------

.. code-block:: console

    $ pip install -e .

Test
----
Tests are run with `pytest <https://pytest.org/>`_.
To run the tests, from the project directory:

.. code-block:: console

    # requirements
    $ pip install -r requirements/test.in

    # update translation
    $ pybabel compile -d src/flask_exts/translations -D admin
    $ pybabel compile -d tests/translations
    
    # test
    $ pytest

Docs
----

.. code-block:: console

    $ pip install -r docs/requirements.txt
    $ cd docs
    $ make html

Publish
--------

.. code-block:: console

    $ python -m build

