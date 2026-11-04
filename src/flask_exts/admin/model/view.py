from collections.abc import Callable, Sequence
from math import ceil
from typing import Any

from flask import (
    abort,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    request,
)
from flask_babel import gettext, lazy_gettext, ngettext

from ...forms.form.flask_form import FlaskForm
from ...security.urls import safe_redirect_target
from ..exposer import expose_action, expose_url
from ..view import View
from .ajax import AjaxModelLoader
from .backend import DataBackend
from .handlers import (
    ExportHandler,
    FilterHandler,
    FormHandler,
    PaginationHandler,
    RowActionHandler,
    RowsActionHandler,
    ValueHandler,
)


class ModelView(View):
    """Admin view for model-backed resources.

    Where the data actually lives (a SQLAlchemy table, a JSON file, a
    filesystem directory, ...) is delegated to a
    :class:`~flask_exts.admin.model.backend.DataBackend`
    instance held on ``self.backend``, supplied via the ``backend_factory``
    constructor argument. This class and its mixins handle everything that
    doesn't depend on that choice: routing, pagination/sort/search argument
    parsing, column/label metadata plumbing, and template rendering.

    Backend-specific subclasses (such as
    :class:`~flask_exts.admin.sqla.view.SqlaModelView`) are expected to
    build the right ``DataBackend`` and pass it (or a factory for it) to
    this constructor; see that class for an example.

    Concrete backend implementations should inherit from this class and provide
    the abstract methods required by the underlying admin layer.

    The class combines column management, filtering, sorting, pagination,
    formatting, forms, CRUD operations, and export support.

    Examples::

        from flask_exts.admin.model import ModelView

        class MyView(ModelView):
            column_list = ('id', 'username', 'email', 'created_at')
            column_sortable_list = ('username', 'created_at')
            form_columns = ('username', 'email', 'password')

    """

    # Permissions

    can_create = True
    """Is model creation allowed"""

    can_edit = True
    """Is model editing allowed"""

    can_delete = True
    """Is model deletion allowed"""

    can_export: bool = False
    """Whether export is enabled for the current view."""

    # Columns

    column_list: list[str] | None = None
    """Collection of the model field names for the list view.

    For example::

        column_list = ('name', 'last_name', 'email')
        # SQLAlchemy model attributes can be used like this:
        column_list = ('name', 'user.last_name')
        # When using SQLAlchemy models, reference related columns
        column_list = ('<relationship>.<related column name>',)
    """

    column_details_list: list[str] | None = None
    """Collection of the field names included in the details view."""

    column_labels: dict[str, str] | None = None
    """Dictionary where key is column name and value is string to display.

    For example::

        column_labels = {"name": "Name", "last_name": "Last Name"}
    """

    column_descriptions: dict[str, str] | None = None
    """Dictionary where key is column name and value is description."""

    column_choices: dict[str, dict[Any, str]] | None = None
    """Map choices to columns in list view.

    Examples::

        column_choices = {
            'my_column': {
                'db_value': 'display_value',
                'db_value2': 'display_value2',
            }
        }
    """

    # value

    column_formatters: dict[str, Callable] | None = None
    """Dictionary of list view column formatters.

    For example, if you want to show price multiplied by
    two, you can do something like this::

        column_formatters = {"price": lambda v, m, p: m.price*2}

    The Callback function has the prototype::

        def formatter(view, model, name):
            # `view` is current administrative view
            # `model` is model instance
            # `name` is property name
            pass
    """

    column_formatters_detail: dict[str, Callable] | None = None
    """Dictionary of list view column formatters to be used for the detail view."""

    column_formatters_export: dict[str, Callable] | None = None
    """Dictionary of list view column formatters to be used for export."""

    column_type_formatters: dict[type, Callable] | None = None
    """Dictionary of value type formatters to be used in the list view.

    If you don't like the default behavior and don't want any type formatters
    applied, just override this property with an empty dictionary::

        column_type_formatters = dict()

    If you want to display `NULL` instead of an empty string, you can do
    something like this. Also comes with bonus `date` formatter::

        from datetime import date
        from .model import typefmt

        def date_format(view, value):
            return value.strftime('%d.%m.%Y')

        MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
        MY_DEFAULT_FORMATTERS.update({
                type(None): typefmt.null_formatter,
                date: date_format
            })

        column_type_formatters = MY_DEFAULT_FORMATTERS

    Type formatters have lower priority than list column formatters.

    The callback function has following prototype::

        def type_formatter(view, value):
            # `view` is current administrative view
            # `value` value to format
            pass
    """

    column_type_formatters_export: dict[type, Callable] | None = None
    """Dictionary of value type formatters to be used in the export."""

    column_type_formatters_detail: dict[type, Callable] | None = None
    """Dictionary of value type formatters to be used in the detail view."""

    # filter

    column_filters = None
    """Collection of the column filters.

    Can contain either field names or instances of
    :class:`~flask_exts.admin.model.filter.filters.BaseFilter`.

    Examples::

        column_filters = ('user', 'email')

    or::

        from .sqla.filters import BooleanEqualFilter

        column_filters = (BooleanEqualFilter(column="user.name", name='Name'),)

    or::

        from ~.sqla.filters import BaseSQLAFilter

        class FilterNameBrown(BaseSQLAFilter):
            def __init__(self, column_type, column, name, data_type=None,
            options=None):
                super().__init__(
                    column_type, column, name, data_type, options=(("1", "Yes"),
                    ("0", "No"))
                )
            def apply(self, query, value):
                if value == "1":
                    return query.add_filter(self.column, "==", "Brown")
                else:
                    return query.add_filter(self.column, "!=", "Brown")

            def operation(self):
                return "is Brown"

        column_filters = [
            FilterNameBrown(
                column_type = get_model_column_type(Author, "last_name"),
                column="author.last_name", name="Last Name",
            ),
        ]
    """

    column_sortable_list: Sequence[str | tuple] | None = None
    """Collection of the sortable columns for the list view.

    For example::

        column_sortable_list = ('name', 'last_name')

    If you want to explicitly specify field/column to be used while
    sorting, you can use a tuple::

        column_sortable_list = ('name', ('user', 'user.username'))

    You can also specify multiple fields to be used while sorting::

        column_sortable_list = (
            'name', ('user', ('user.first_name', 'user.last_name')))
    """

    column_default_sort: str | tuple[str, bool] | list[tuple[str, bool]] | None = None
    """Default sort column if no sorting is applied.

    Examples::

        column_default_sort = 'user'

    You can use tuple to control ascending descending order. In following example, items
    will be sorted in descending order::

        column_default_sort = ('user', True)

    If you want to sort by more than one column,
    you can pass a list of tuples::

        column_default_sort = [('name', True), ('last_name', True)]
    """

    column_searchable_list: Sequence[str] | None = None
    """A collection of the searchable columns.

    It is assumed that only text-only fields are searchable, but it is up to the
    model implementation to decide.

    Examples::

        column_searchable_list = ('name', 'email')

    You can also pass relation.column::

        column_searchable_list = (user.name, user.email)
    """

    column_editable_list = None
    """Collection of the columns which can be edited from the list view.

    For example::

        column_editable_list = ('name', 'last_name')
    """

    # Forms
    base_form_class = FlaskForm

    create_form_columns: list | None = None

    form_columns: list | None = None
    """List of form fields to include.

    Examples::

        form_columns = ('name', 'email')
    """

    form_excluded_columns: list | None = None
    """Collection of excluded form field names.

    For example::

        form_excluded_columns = ('last_name', 'email')
    """

    form_widget_args: dict[str, dict[str, Any]] | None = None
    """Dictionary of form widget rendering arguments.

    Use this to customize how widget is rendered without using custom template.

    Examples::

        form_widget_args = {
            'description': {
                'rows': 10, 'style': 'color: black'
            }, 'other_field': {
                'disabled': True
            }
        }

    Changing the format of a DateTimeField will require changes to both
    form_widget_args and form_args.

    Examples::

        form_args = {
            "start": {"format": "%Y-%m-%d %I:%M %p"} # changes how the input is
            parsed by strptime (12 hour time)
        } form_widget_args = {
            "start": {
                'data-date-format': u'yyyy-mm-dd HH:ii P', 'data-show-meridian':
                'True'
            } # changes how the DateTimeField displays the time
        )
    """

    form_extra_fields = None
    """Additional field definitions for the form.

    Examples::

        form_extra_fields = {
            'password': PasswordField('Password')
        }

    You can control order of form fields using ``form_columns`` property. For
    example::

        form_columns = ('name', 'email', 'password', 'secret')

        form_extra_fields = {
            'password': PasswordField('Password')
        }

    In this case, password field will be put between email and secret fields
    that are autogenerated.
    """

    form_args: dict[str, dict[str, Any]] = None
    """Dictionary of form field arguments.

    Refer to WTForms documentation for list of possible options.

    Examples::

        from wtforms.validators import DataRequired
        form_args = {
            "name": {"label": "First Name", "validators": [DataRequired()]}
        }
    """

    ajax_refs: dict[str, Any] | None = None
    """AJAX-related form references.

    Should contain dictionary, where key is field name and value is either a
    dictionary which configures AJAX lookups or backend-specific
    `AjaxModelLoader` class instance.

    For example, it can look like::

        ajax_refs = {
            'user': {
                'fields': ('first_name', 'last_name', 'email'), 'placeholder':
                'Please select', 'page_size': 10, 'minimum_input_length': 0,
            }
        }

    Or with SQLAlchemy backend like this::

        ajax_refs = {
            'user': AjaxSqlaModelLoader('user', User, self.session,
            fields=['email'], page_size=10)
        }
    """

    form_choices: dict[str, list[tuple[str, str]]] | None = None
    """Map choices to form fields

    Examples::

        form_choices = {'my_form_field': [
            ('db_value', 'display_value'),
        ]}
    """

    action_disallowed_list: tuple[str] = ()
    """Set of disallowed action names."""

    # Export

    column_export_list: list[str] | None = None
    """Collection of the field names included in the export."""

    export_max_rows: int = 10000
    """Maximum number of rows allowed for export."""

    export_types: tuple[str] = ("csv",)
    """A list of available export filetypes. `csv` only is default."""

    page_size: int = 20
    """Default page size for pagination."""

    can_set_page_size = True
    """Allows to select page size via dropdown list."""

    page_size_options: tuple = (5, 10, 20, 50, 100)
    """Sets the page size options available, if `can_set_page_size` is True."""

    # Templates
    list_template = "admin/model/list.html"
    """Default list view template"""

    edit_template = "admin/model/edit.html"
    """Default edit template"""

    create_template = "admin/model/create.html"
    """Default create template"""

    details_template = "admin/model/details.html"
    """Default details view template"""

    def __init__(
        self,
        model,
        backend_factory: Callable[..., DataBackend],
        name=None,
        endpoint=None,
        url=None,
        **kwargs,
    ):
        """Constructor.

        Args:
            backend_factory:
                Callable that receives this view instance and returns a
                :class:`DataBackend` instance. A factory (rather than an
                already-built backend) is required because most backends need to
                read view-level configuration that only exists once ``self`` is
                constructed.
            name:
                View name. If not provided, will use the model class name
            endpoint:
                Base endpoint. If not provided, will use the model name.
            url:
                Base URL. If not provided, will use endpoint as a URL.
        """
        self.model = model
        self._init_base(model, name, endpoint, url)
        self._init_backend(model, backend_factory, **kwargs)
        self._init_columns()
        self._init_handlers()
        self._init_components(**kwargs)

    def _init_base(self, model, name, endpoint, url):
        if name is None:
            name = model.__name__.lower()
        if endpoint is None:
            endpoint = model.__name__.lower()
        super().__init__(name, endpoint, url)

    def _init_backend(self, model, backend_factory, **kwargs):
        self._backend = backend_factory(model, self, **kwargs)

    def _init_columns(self):
        # list_columns
        list_columns = self.column_list or self._backend.scaffold_list_columns()
        self._list_columns = self.get_column_names(list_columns)

        # detail_columns
        if self.column_details_list is not None:
            self._details_columns = self.get_column_names(self.column_details_list)
        else:
            self._details_columns = self._list_columns

        # export_columns
        self._export_columns = self.get_column_names(
            self.column_export_list or list_columns
        )

        # sortable_columns
        column_sortable_list = (
            self.column_sortable_list or self._backend.scaffold_sortable_columns()
        )
        self._sortable_columns = {}
        for c in column_sortable_list:
            if isinstance(c, tuple):
                self._sortable_columns[c[0]] = c[1]
            else:
                self._sortable_columns[c] = c

        # column_default_sort
        if self.column_default_sort:
            if isinstance(self.column_default_sort, list):
                self._column_default_sort = self.column_default_sort
            elif isinstance(self.column_default_sort, tuple):
                self._column_default_sort = [self.column_default_sort]
            else:
                self._column_default_sort = [(self.column_default_sort, False)]
        else:
            self._column_default_sort = None

        # Process AJAX reference configuration into model loaders
        self._ajax_refs = {}
        if self.ajax_refs:
            for name, options in self.ajax_refs.items():
                if isinstance(options, AjaxModelLoader):
                    self._ajax_refs[name] = options
                else:
                    if ajax_loader := self.create_ajax_loader(name, options):
                        self._ajax_refs[name] = ajax_loader

    def _init_handlers(self):
        self._pagination_handler = PaginationHandler(self)
        self._rowactions_handler = RowActionHandler(self)
        self._rowsaction_handler = RowsActionHandler(self)
        self._filter_handler = FilterHandler(self)
        self._form_handler = FormHandler(self)
        self._export_handler = ExportHandler(self)
        self._value_handler = ValueHandler(self)

    def _init_components(self, **kwargs):
        """Initialize the list, sort, detail, export, and form metadata."""

    # --- Delegation to the data backend -----------------------------------
    #
    # These are thin, explicit forwarders rather than a __getattr__ catch-all:
    # each one is independently discoverable, documented, and type-hintable,
    # matching how BaseModelView's mixins already document their abstract
    # hooks (see e.g. admin/model/operations/read.py).

    def scaffold_filter(self, column_path):
        return self._backend.scaffold_filter(column_path)

    def scaffold_form(self, form_type=None):
        return self._backend.scaffold_form(form_type)

    def scaffold_list_form(self, validators=None):
        return self._backend.scaffold_list_form(validators=validators)

    def get_one(self, id):
        return self._backend.get_one(id)

    def get_list(
        self,
        search=None,
        filters=None,
        sort_field=None,
        sort_desc=None,
        page=None,
        page_size=None,
    ):
        return self._backend.get_list(
            search=search,
            filters=filters,
            sort_field=sort_field,
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
        )

    def get_pk_value(self, obj):
        return self._backend.get_pk_value(obj)

    def create_model(self, model):
        return self._backend.create_model(model)

    def update_model(self, model):
        return self._backend.update_model(model)

    def delete_model(self, model):
        return self._backend.delete_model(model)

    def delete_model_by_pk_ids(self, ids):
        return self._backend.delete_model_by_pk_ids(ids)

    def create_ajax_loader(self, name, options):
        return self._backend.create_ajax_loader(name, options)

    # --- Delegation to the handlers -----

    def get_row_actions(self):
        return self._rowactions_handler.get_row_actions()

    def get_default_page_size(self):
        return self._pagination_handler.get_default_page_size()

    def get_list_args(self):
        return self._pagination_handler.get_list_args()

    def get_list_url(self, view_args):
        return self._pagination_handler.get_list_url(view_args)

    def get_safe_page_size(self, page_size):
        return self._pagination_handler.get_safe_page_size(page_size)

    def get_list_actions(self):
        return self._rowsaction_handler.get_list_actions()

    def get_rows_action(self, name):
        return self._rowsaction_handler.get_action(name)

    def action_form(self, *args, **kwargs):
        return self._rowsaction_handler.action_form(*args, **kwargs)

    def get_filters(self):
        return self._filter_handler.get_filters()

    def get_filter_groups(self):
        return self._filter_handler.get_filter_groups()

    def get_active_filters(self):
        return self._filter_handler.get_active_filters()

    def get_active_filters_kwargs(self, active_filters):
        return self._filter_handler.get_active_filters_kwargs(active_filters)

    def get_ajax_loader(self, name):
        return self._ajax_refs.get(name)

    def get_list_value(self, model, name):
        return self._value_handler.get_list_value(model, name)

    def get_detail_value(self, model, name):
        return self._value_handler.get_detail_value(model, name)

    def get_export_value(self, model, name):
        return self._value_handler.get_export_value(model, name)

    def create_form(self, *args, **kwargs):
        return self._form_handler.create_form(*args, **kwargs)

    def edit_form(self, *args, **kwargs):
        return self._form_handler.edit_form(*args, **kwargs)

    def delete_form(self, *args, **kwargs):
        return self._form_handler.delete_form(*args, **kwargs)

    def list_form(self, *args, **kwargs):
        return self._form_handler.list_form(*args, **kwargs)

    def export_file(self, export_type, return_url):
        if export_type == "csv":
            return self._export_handler.export_csv(return_url)
        else:
            return self._export_handler.export_tablib(export_type, return_url)

    # --- View functions -----------------------------------

    def get_save_return_url(self, model, is_created: bool = False) -> str:
        """Return the URL the user is redirected to after a successful save.

        Args:
            model: Saved object.
            is_created: Whether the object was newly created.

        Returns:
            str: A redirect URL.
        """
        return self.get_url(".details_view", id=model.id)

    def _prettify_name(self, name: str) -> str:
        """Convert a field name into a readable display label.

        For example, ``user_name`` becomes ``User Name``.

        Args:
            name: Field name.

        Returns:
            str: Human-readable label.
        """
        return name.replace("_", " ").title()

    def get_column_label(self, column_name: str, default_label=None) -> str:
        """Return a human-readable column label.

        If a label is defined in ``column_labels``, it is used; otherwise, the
        field name is converted into a display label.

        Args:
            column_name: Model field name.

        Returns:
            str: A formatted display label.
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]

        if default_label:
            return default_label

        return self._prettify_name(column_name)

    def get_column_description(self, column_name: str):
        if not self.column_descriptions:
            return None
        return self.column_descriptions.get(column_name)

    def search_placeholder(self) -> str | None:
        """Build a search placeholder from the searchable column labels.

        Returns:
            str | None: A label string such as ``"Name, Email"`` or ``None``
                when no searchable columns are configured.
        """
        if not self.column_searchable_list:
            return None

        placeholders = [
            self.get_column_label(searchable, searchable)
            for searchable in self.column_searchable_list
        ]

        return ", ".join(placeholders)

    def get_column_names(self, columns: list[str]) -> list[tuple[str, str]]:
        """Return column pairs of ``(field_name, label)`` for the given columns.

        Args:
            columns: List of columns to include.

        Returns:
            list[tuple[str, str]]: A list of ``(field_name, label)`` tuples.
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self) -> list[tuple[str, str]]:
        """Return the columns displayed in the list view.

        Returns:
            list[tuple[str, str]]: ``(field_name, label)`` .
        """
        return self._list_columns

    def get_details_columns(self) -> list[tuple[str, str]]:
        """Return the columns displayed in the detail view.

        Returns:
            list[tuple[str, str]]: ``(field_name, label)``.
        """
        return self._details_columns

    def get_export_columns(self) -> list[tuple[str, str]]:
        """Return the columns used in export output.

        Returns:
            list[tuple[str, str]]: ``(field_name, label)`` pairs for export.
        """
        return self._export_columns

    def get_sortable_columns(self):
        return self._sortable_columns

    def get_default_order(self) -> list[tuple[str, bool]] | None:
        """Return the default sort order for the current view.

        Returns:
            list[tuple[str, bool]] | None: A list of ``(column_name, desc)``
        """
        return self._column_default_sort

    def is_sortable(self, name: str) -> bool:
        """Return whether a column name is sortable.

        Args:
            name: Column name to evaluate.

        Returns:
            bool: ``True`` when the column is sortable, otherwise ``False``.
        """
        return name in self._sortable_columns

    def _get_column_by_idx(self, idx: int | None) -> tuple[str, str] | None:
        """Return a column tuple by index.

        Args:
            idx: Column index in the list view.

        Returns:
            tuple[str, str] | None: A ``(field_name, label)`` tuple or
                ``None`` if the index is invalid.
        """
        if idx is None or idx < 0 or idx >= len(self._list_columns):
            return None

        return self._list_columns[idx]

    def is_editable(self, name: str) -> bool:
        """Return whether the given column is editable.

        Args:
            name: Column name.

        Returns:
            bool: ``True`` when the column is editable.
        """
        return (
            self.can_edit
            and self.column_editable_list is not None
            and name in self.column_editable_list
        )

    def is_action_allowed(self, name: str) -> bool:
        """Return whether an action is allowed for the current view."""
        if name == "delete" and not self.can_delete:
            return False
        if name in self.action_disallowed_list:
            return False
        return (
            super().is_action_allowed(name)
            if hasattr(super(), "is_action_allowed")
            else True
        )

    def get_redirect_target(self, param_name="url", endpoint=".index_view"):
        """Return the target URL used for redirects."""
        return safe_redirect_target(
            request.values.get(param_name), self.get_url(endpoint)
        )

    @expose_url("/")
    def index_view(self):
        # Grab parameters from URL
        view_args = self.get_list_args()

        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        page_size = self.get_safe_page_size(view_args.page_size)

        count, data = self.get_list(
            search=view_args.search,
            filters=view_args.filters,
            sort_field=sort_column,
            sort_desc=view_args.sort_desc,
            page=view_args.page,
            page_size=page_size,
        )

        if count is not None and page_size:
            num_pages = ceil(count / float(page_size))
        elif not page_size:
            num_pages = 0
        else:
            num_pages = None

        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None
            return self.get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1
            return self.get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def page_size_url(s):
            return self.get_list_url(view_args.clone(page_size=s))

        clear_search_url = self.get_list_url(
            view_args.clone(
                page=0,
                sort=view_args.sort,
                sort_desc=view_args.sort_desc,
                search=None,
                filters=None,
            )
        )

        return self.render(
            self.list_template,
            data=data,
            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            # sort
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,
            # search
            clear_search_url=clear_search_url,
            search=view_args.search,
            # filter
            active_filters=view_args.filters,
            filter_args=self.get_active_filters_kwargs(view_args.filters),
            # misc
            return_url=self.get_list_url(view_args),
            extra_args=view_args.extra_args,
        )

    @expose_url("/new/", methods=("GET", "POST"))
    def create_view(self):
        """Create model view"""
        return_url = self.get_redirect_target()

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()

        if form.validate_on_submit():
            model_instance = self.model()
            form.populate_obj(model_instance)
            model = self.create_model(model_instance)
            if model:
                flash(gettext("Record was successfully created."), "success")
                if "_add_another" in request.form:
                    return redirect(request.url)
                elif "_continue_editing" in request.form:
                    if model is not True:
                        url = self.get_url(
                            ".edit_view",
                            id=self.get_pk_value(model),
                            url=return_url,
                        )
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    return redirect(self.get_save_return_url(model, is_created=True))
            else:
                flash(gettext("Failed to create record."), "error")

        form_opts = {"widget_args": self.form_widget_args}

        return self.render(
            self.create_template, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        """Edit model view"""
        return_url = self.get_redirect_target()

        if not self.can_edit:
            return redirect(return_url)

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        form = self.edit_form(obj=model)

        if form.validate_on_submit():
            form.populate_obj(model)

            if self.update_model(model):
                flash(gettext("Record was successfully saved."), "success")
                if "_add_another" in request.form:
                    return redirect(self.get_url(".create_view", url=return_url))
                elif "_continue_editing" in request.form:
                    return redirect(
                        self.get_url(".edit_view", id=self.get_pk_value(model))
                    )
                else:
                    return redirect(self.get_save_return_url(model, is_created=False))
            else:
                flash(gettext("Failed to update record."), "error")

        form_opts = {"widget_args": self.form_widget_args}

        template = self.edit_template

        return self.render(
            template,
            model=model,
            form=form,
            form_opts=form_opts,
            return_url=return_url,
        )

    @expose_url("/details/")
    def details_view(self):
        """Details model view"""
        return_url = self.get_redirect_target()

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        template = self.details_template

        return self.render(
            template,
            model=model,
            details_columns=self._details_columns,
            return_url=return_url,
        )

    @expose_url("/delete/", methods=("POST",))
    def delete_view(self):
        """Delete model view. Only POST method is allowed."""
        return_url = self.get_redirect_target()
        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()
        if form.validate():
            id = form.id.data
            model = self.get_one(id)
            if model is None:
                flash(gettext("Record does not exist."), "error")
                return redirect(return_url)

            if self.delete_model(model):
                count = 1
                flash(
                    ngettext(
                        "Record was successfully deleted.",
                        "%(count)s records were successfully deleted.",
                        count,
                        count=count,
                    ),
                    "success",
                )
                return redirect(return_url)
            else:
                flash(gettext("Failed to delete record."), "error")
        else:
            if hasattr(form, "flash_errors"):
                form.flash_errors(message="Failed to delete record. %(error)s")

        return redirect(return_url)

    @expose_url("/ajax/lookup/")
    def ajax_lookup(self):
        name = request.args.get("name")
        query = request.args.get("query")
        offset = request.args.get("offset", type=int)
        limit = min(max(1, request.args.get("limit", 10, type=int)), 100)
        loader = self.get_ajax_loader(name)
        if not loader:
            abort(404)
        data = [loader.format(m) for m in loader.get_list(query, offset, limit)]
        return jsonify(data)

    @expose_url("/ajax/update/", methods=("POST",))
    def ajax_update(self):
        if not self.column_editable_list:
            abort(404)
        if not request.is_json:
            abort(404)

        json_data = request.get_json()
        form = self.list_form()
        # Delete non-submitted fields to prevent validation issues.
        for field in list(form):
            if field.name in json_data or field.name == "csrf_token":
                pass
            else:
                form.__delitem__(field.name)

        if form.validate_on_submit():
            pk = form.pk.data
            record = self.get_one(pk)

            if record is None:
                return gettext("Record does not exist."), 500

            form.populate_obj(record)

            if self.update_model(record):
                return gettext("Record was successfully saved.")
            else:
                msgs = ", ".join([msg for msg in get_flashed_messages()])
                return gettext("Failed to update record. %(error)s", error=msgs), 500
        else:
            for field in form:
                for error in field.errors:
                    if isinstance(error, list):
                        return (
                            gettext(
                                "Failed to update record. %(error)s",
                                error=", ".join(error),
                            ),
                            500,
                        )
                    else:
                        return (
                            gettext(
                                "Failed to update record. %(error)s",
                                error=error,
                            ),
                            500,
                        )

        return gettext("Validation failed."), 400

    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """Mass-model action."""
        form = self.action_form()
        action_name = form.action.data
        if not self.is_action_allowed(action_name):
            raise ValueError(f"Action {action_name!r} is not allowed")
        if (handler := self.get_rows_action(action_name)) is None:
            raise ValueError(f"No action found for {action_name}")

        if form.validate():
            ids = request.form.getlist("rowid")
            response = handler(ids)
            if response is not None:
                return response
        else:
            form.flash_errors(message="Failed to perform action. %(error)s")

        return redirect(self.get_redirect_target())

    @expose_action(
        "delete",
        lazy_gettext("Delete"),
        lazy_gettext("Are you sure you want to delete selected records?"),
    )
    def action_delete(self, ids: list):
        count = self.delete_model_by_pk_ids(ids)
        flash(
            ngettext(
                "Record was successfully deleted.",
                "%(count)s records were successfully deleted.",
                count,
                count=count,
            ),
            "success",
        )

    @expose_url("/export/<export_type>/")
    def export(self, export_type: str):
        """Handle export requests for a given file format.

        Args:
            export_type: Output format to generate.

        Returns:
            Response: File response or redirect.
        """
        return_url = (
            self.get_redirect_target() if hasattr(self, "get_redirect_target") else "#"
        )

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext("Permission denied."), "error")
            return redirect(return_url)

        return self.export_file(export_type, return_url)
