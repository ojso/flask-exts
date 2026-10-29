ModelView
=========

This page documents how Flask-Exts's admin model views are put together:
the ``ModelView`` / ``DataBackend`` split, how ``SqlaModelView`` uses it,
and the configuration attributes you'll use most often.

Overview
--------

:class:`~flask_exts.admin.model.view.ModelView` is the base admin view for
any model-backed resource (a database table, a JSON file, a filesystem
directory, ...). It owns everything that doesn't depend on where the data
actually lives: URL routing, pagination/sort/search argument parsing,
column and label metadata, template rendering, and form field wrapping.

Where the data lives, and how records are actually read and written, is
delegated to a :class:`~flask_exts.admin.model.backend.DataBackend`
instance held on ``self.backend``. ``ModelView`` doesn't inherit from a
backend-specific base class; it holds a backend through composition and
forwards the handful of data-access calls (``get_list``, ``create_model``,
``scaffold_form``, ...) to it.

:class:`~flask_exts.admin.sqla.view.SqlaModelView` is the concrete,
SQLAlchemy-backed subclass most projects use directly. It builds a
:class:`~flask_exts.admin.sqla.backend.SqlaBackend` in its constructor and
passes a factory for it up to ``ModelView``::

    from flask_exts.admin.sqla.view import SqlaModelView

    class AuthorView(SqlaModelView):
        column_list = ["id", "name", "email"]

    authorview = AuthorView(Author)
    admin.register_view(authorview)

If you need a different data source (a JSON file, a filesystem directory,
...), you write a new :class:`~flask_exts.admin.model.backend.DataBackend`
implementation and a thin ``ModelView`` subclass that builds one -- you
don't need to reimplement routing, pagination, or template rendering.

The ``DataBackend`` protocol
-----------------------------

A backend implements:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Method
     - Responsibility
   * - ``scaffold_list_columns()``
     - Field names to show in the list view.
   * - ``scaffold_sortable_columns()``
     - Mapping of sortable column name to the field(s) used to sort by.
   * - ``scaffold_filter(column_path)``
     - Filter objects available for a column, or ``None``.
   * - ``scaffold_form()``
     - Form class for creating/editing a record.
   * - ``scaffold_list_form(validators=None)``
     - Form class for inline editing from the list view.
   * - ``get_list(page, sort_field, sort_desc, search, filters, page_size=None)``
     - ``(count, rows)`` for one page of results.
   * - ``get_one(id)``
     - A single record by primary key, or ``None``.
   * - ``get_pk_value(obj)``
     - String representation of a record's primary key.
   * - ``create_model(form)`` / ``update_model(form, model)`` / ``delete_model(model)``
     - Write operations driven by a validated form.
   * - ``delete_model_by_pk_ids(ids)``
     - Bulk delete; returns the number of records removed.
   * - ``create_ajax_loader(name, options)``
     - Optional. Only needed if the backend supports ``ajax_refs``.

A backend is constructed with the ``ModelView`` instance it belongs to
(``DataBackend.__init__(self, view)``), so it can read public, view-level
configuration -- ``view.column_searchable_list``, ``view._filters``,
``view.page_size``, and so on -- without that state being duplicated on the
backend itself. How search/filter/sort/pagination are actually carried out
internally is entirely up to the backend: :class:`SqlaBackend` builds a
SQL query (see ``_apply_search``, ``_apply_filters``, ``_apply_sorting``,
``_apply_pagination``, ``_apply_auto_joins`` for its approach), but a
JSON-file or filesystem backend might just filter, sort, and slice an
in-memory list -- the protocol only constrains ``get_list()``'s inputs and
outputs, not any intermediate steps.

Inline models (parent/child relationships), AJAX foreign-key lookups
beyond the ``create_ajax_loader`` hook, and other relational-data-specific
features are **not** part of the generic protocol -- they live directly on
:class:`SqlaModelView` (see `Inline models`_ below), since a JSON or
filesystem backend has no equivalent concept.

Creating a view
----------------

::

    from flask_exts.admin.sqla.view import SqlaModelView

    class PostView(SqlaModelView):
        column_list = ["id", "author", "title", "date"]
        column_searchable_list = ["title"]
        column_sortable_list = ["id", "title", "date"]
        column_default_sort = ("date", True)
        can_export = True

    postview = PostView(Post)
    admin.register_view(postview)

``SqlaModelView.__init__(model, session=None, name=None, endpoint=None, url=None, static_folder=None)``
takes the SQLAlchemy model class as its only required argument. ``name``
defaults to the model's class name, ``endpoint`` to the lowercased name,
and ``session`` to the shared ``db.session`` (see :doc:`database`) unless
you pass a different one explicitly.

Columns, sorting, searching, filtering
----------------------------------------

These are configured as class attributes, resolved against the model when
the view is constructed:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Attribute
     - Description
   * - ``column_list``
     - Columns shown in the list view. Supports dotted paths into
       relationships (``"author.email"``). Defaults to every scalar
       column on the model if unset.
   * - ``column_labels``
     - ``{"column_name": "Display Label"}`` overrides for list/detail/form
       headers.
   * - ``column_sortable_list``
     - Which columns can be sorted. Entries can be a plain name, a
       ``(label, column_path)`` tuple, or a
       ``(label, (path1, path2, ...))`` tuple to sort by multiple columns
       at once.
   * - ``column_default_sort``
     - Sort applied when no explicit sort is requested. A column name, a
       ``(column, descending)`` tuple, or a list of such tuples for a
       multi-column default sort.
   * - ``column_searchable_list``
     - Columns included in free-text search, including dotted relationship
       paths (``"author.last_name"``).
   * - ``column_filters``
     - Columns (or explicit filter instances) exposed as list-view
       filters. Each scalar column generates several operators
       automatically (contains/equals/empty/in list/..., depending on
       type); pass a filter instance directly for custom operators.
   * - ``column_editable_list``
     - Columns that can be edited inline from the list view via the
       ``/ajax/update/`` route, without opening the edit page.
   * - ``column_choices``
     - ``{"column_name": {"db_value": "display_value", ...}}`` to map raw
       values to display labels in the list view.
   * - ``column_details_list`` / ``column_export_list``
     - Separate column sets for the details view and CSV/tablib export,
       when they should differ from ``column_list``.

See the attribute docstrings on
:class:`~flask_exts.admin.model.base.BaseModelView` for the full list,
including the formatter hooks (``column_formatters``,
``column_formatters_export``, ``column_formatters_detail``,
``column_type_formatters``).

Pagination
----------

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Attribute
     - Description
   * - ``page_size``
     - Default page size. ``20`` unless overridden.
   * - ``can_set_page_size``
     - Whether a visitor can change the page size via ``?page_size=``.
       ``True`` by default.
   * - ``page_size_options``
     - Allowed page sizes when ``can_set_page_size`` is ``True``. Requests
       for a size outside this tuple fall back to ``page_size``.

Forms
-----

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Attribute
     - Description
   * - ``form_columns`` / ``form_excluded_columns``
     - Include or exclude a subset of model fields from the generated
       create/edit form. If both are unset, every model column is
       included.
   * - ``form_args``
     - WTForms field keyword arguments (labels, validators, ...), keyed by
       field name.
   * - ``form_widget_args``
     - Widget-rendering keyword arguments (``rows``, ``disabled``, custom
       ``data-*`` attributes), keyed by field name.
   * - ``form_extra_fields``
     - Extra WTForms fields with no corresponding model column (e.g. a
       password field for a hashed column). Combine with ``form_columns``
       to control where they appear.
   * - ``ajax_refs``
     - AJAX-backed foreign-key lookups. See `AJAX foreign keys`_ below.
   * - ``base_form_class``
     - The form base class used when scaffolding; override to add
       cross-field validation or shared behavior.

AJAX foreign keys
~~~~~~~~~~~~~~~~~

::

    class PostView(SqlaModelView):
        ajax_refs = {
            "author": {
                "fields": ("first_name", "last_name"),
                "placeholder": "Please select",
                "minimum_input_length": 0,
                "page_size": 10,
            },
        }

This replaces a plain foreign-key select field with an incrementally
loaded, search-as-you-type widget backed by the view's ``/ajax/lookup/``
route. ``fields`` lists which columns on the related model are matched
against the typed query.

Inline models
--------------

``SqlaModelView`` (not the generic ``DataBackend`` protocol) supports
editing parent/child relationships from the parent's form, via
``inline_models``::

    class AuthorView(SqlaModelView):
        inline_models = (Post,)

Related rows are managed independently through AJAX
(``/ajax/create-parent/`` and ``/ajax/inline/<relationship_name>/``): a new
parent record is created first, and its inline rows are then added, edited,
or removed without a full form resubmission. ``inline_models`` accepts:

- a child model class directly: ``inline_models = (Post,)``
- a ``(model, options)`` pair: ``inline_models = [(Post, {"form_columns": ["title"]})]``
- an ``InlineForm`` instance for more control over the generated sub-form::

      from flask_exts.admin.sqla.form.inline_form import InlineForm

      class MyInlineForm(InlineForm):
          form_columns = ("title", "date")

      class AuthorView(SqlaModelView):
          inline_models = (MyInlineForm(Post),)

By default, inline models assume a many-to-many-style collection
relationship. For a one-to-one relationship, set
``inline_model_converter = InlineOneToOneModelConverter`` on the
``InlineForm``.

Export
------

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Attribute
     - Description
   * - ``can_export``
     - Enables the ``/export/<export_type>/`` route. ``False`` by default.
   * - ``export_types``
     - Formats offered, e.g. ``("csv", "xls")``. Anything `tablib
       <https://tablib.readthedocs.io/en/stable/formats.html>`_ supports
       besides ``csv`` is available if the optional dependency is
       installed.
   * - ``export_max_rows``
     - Row limit applied to the export query. ``10000`` by default.

Permissions
-----------

``can_create``, ``can_edit``, and ``can_delete`` (all ``True`` by default)
gate the corresponding routes at the view level: when ``False``, the
route redirects back to the list view instead of performing the action.

This is a separate, narrower check from the application-wide authorizer
(:class:`~flask_exts.security.authorizer.simple_authorizer.SimpleAuthorizer`),
which decides whether a user can reach the view at all. A view can be
reachable by a logged-in user but still refuse to create or delete
records if these flags say so.

Templates
---------

``list_template``, ``create_template``, ``edit_template``, and
``details_template`` point at the Jinja templates used for each route
(``admin/model/list.html`` and friends by default). Override them on a
subclass to customize rendering without touching the view logic.

API reference
--------------

.. automodule:: flask_exts.admin.model.backend
   :members:

.. automodule:: flask_exts.admin.model.view
   :members:

.. automodule:: flask_exts.admin.sqla.backend
   :members:

.. automodule:: flask_exts.admin.sqla.view
   :members:
