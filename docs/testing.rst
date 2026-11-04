Testing
=======

This guide covers running tests, test-writing conventions, integration-test
models, and validation.

Running tests
-------------

The project uses `pytest <https://pytest.org/>`_. From the project root, with
the repository virtual environment activated, run the full test suite:

.. code-block:: console

    $ python -m pytest -q

Run a single file or test case while iterating:

.. code-block:: console

    $ python -m pytest -q tests/unit/forms/fields/test_json.py
    $ python -m pytest -q tests/unit/forms/fields/test_json.py::test_json_field

The ``make test`` and ``make coverage`` targets also work, but they call
``pytest`` and ``coverage`` directly, so the virtual environment must be
activated first.

Test organization
-----------------

Put isolated logic tests in ``tests/unit/``. Put tests that require Flask,
application configuration, a database, or integration between components in
``tests/integration/``. Group tests by feature or behavior, splitting modules
when they mix unrelated concerns while avoiding tiny modules that fragment a
cohesive test area.

Reuse fixtures from ``tests/conftest.py`` and existing helpers when they
express shared setup or behavior. Reset shared state, register strict pytest
markers, and avoid network or external-service dependencies. Do not rely on
execution order or state left by another test; create the records and
relationships each test needs.

Keep each test focused on one scenario. Use separate tests for distinct
behaviors or materially different conditions, and avoid redundant coverage or
one-off abstractions.

Test names
----------

Use descriptive names in the form
``test_<feature>_<scenario>[_<condition>]``, for example
``test_bulk_delete_with_composite_primary_key``. Describe the behavior and
relevant condition rather than implementation details or generic labels such
as ``test_model``, ``test_data``, or ``test_case``. Use consistent, unambiguous
terms such as ``primary_key`` and ``one_to_one``.

Ensure intended tests are collected by pytest. In particular, do not put
coverage in helpers whose names start with ``_test_`` or otherwise exclude
them from collection. When tests are renamed or moved, preserve their behavior
and verify they remain collected.

Assertions and coverage
-----------------------

Assert observable outcomes such as response status and relevant content,
returned values, validation errors, or persisted state. Include meaningful
success, failure, and boundary-condition assertions as appropriate, and avoid
assertions unrelated to the scenario. Similar assertions are appropriate
when they cover distinct configurations, request paths, or regression
conditions.

Integration test models and database state
-------------------------------------------

Define reusable SQLAlchemy models in a ``models/`` package near the
integration tests that use them. For admin SQLAlchemy tests, use
``tests/integration/admin/sqla/models/``; move models to a broader integration
test package only when multiple test areas genuinely share them. Organize
model modules by purpose or relationship pattern.

Use descriptive ``snake_case`` module and table names, PascalCase model class
names ending in ``Model``, and descriptive field and relationship names.
Avoid generic class names such as ``Model1``, ``Child``, or ``Tree``. Keep
table names unique and update foreign-key targets and test references
consistently when renaming tables or fields.

The integration-test ``db`` and its ``db.Model.metadata`` are shared
singletons. Import canonical model classes rather than redefining models or
tables in individual test modules. Remember that ``db.reset_all()`` drops and
recreates every table registered in the shared metadata, not only the current
test's tables.

Validation
----------

Run the smallest relevant test target while iterating. Run the broader
affected test directory when changes span multiple test modules or shared
setup, and run the full suite for broad changes. Run Ruff checks for changed
Python files and check the diff for whitespace errors. Do not reformat
unrelated files to resolve pre-existing issues.
