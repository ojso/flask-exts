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

    $ pip install -r requirements/test.in
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

