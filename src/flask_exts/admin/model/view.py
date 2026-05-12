import warnings
import csv
import mimetypes
import time
from typing import Optional
from math import ceil
from functools import reduce
import tablib
from flask import request
from flask import redirect
from flask import flash
from flask import abort
from flask import Response
from flask import jsonify
from flask import get_flashed_messages
from flask import stream_with_context
from werkzeug.utils import secure_filename
from wtforms.fields import HiddenField
from wtforms.validators import ValidationError, InputRequired
from flask_babel import gettext, ngettext
from ..view import View
from .actions import ActionsMixin
from .rowaction import RowActionMixin
from .filter_mixin import FilterMixin
from ..exposer import expose_url
from .types import T_COLUMN_LIST, T_FORMATTERS
from .typefmt import BASE_FORMATTERS, EXPORT_FORMATTERS, DETAIL_FORMATTERS
from .ajax import AjaxModelLoader

class ViewArgs:
    """
    List view arguments.
    """

    def __init__(
        self,
        page=None,
        page_size=None,
        sort=None,
        sort_desc=None,
        search=None,
        filters=None,
        extra_args=None,
    ):
        self.page = page
        self.page_size = page_size
        self.sort = sort
        self.sort_desc = bool(sort_desc)
        self.search = search
        self.filters = filters

        if not self.search:
            self.search = None

        self.extra_args = extra_args or dict()

    def clone(self, **kwargs):
        if self.filters:
            flt = list(self.filters)
        else:
            flt = None

        kwargs.setdefault("page", self.page)
        kwargs.setdefault("page_size", self.page_size)
        kwargs.setdefault("sort", self.sort)
        kwargs.setdefault("sort_desc", self.sort_desc)
        kwargs.setdefault("search", self.search)
        kwargs.setdefault("filters", flt)
        kwargs.setdefault("extra_args", dict(self.extra_args))

        return ViewArgs(**kwargs)



class ModelView(View, ActionsMixin, RowActionMixin, FilterMixin):
    """
    Model view.

    This view does not make any assumptions on how models are stored or managed, but expects the following:

        1. The provided model is an object
        2. The model contains properties
        3. Each model contains an attribute which uniquely identifies it (i.e. a primary key for a database model)
        4. It is possible to retrieve a list of sorted models with pagination applied from a data source
        5. You can get one model by its identifier from the data source

    Essentially, if you want to support a new data store, all you have to do is:

        1. Derive from the `ModelView` class
        2. Implement various data-related methods (`get_list`, `get_one`, `create_model`, etc)
        3. Implement automatic form generation from the model representation (`scaffold_form`)
    """

    # Permissions
    can_create = True
    """Is model creation allowed"""

    can_edit = True
    """Is model editing allowed"""

    can_delete = True
    """Is model deletion allowed"""

    can_export = False
    """Is model list export allowed"""

    # Templates
    list_template = "admin/model/list.html"
    """Default list view template"""

    edit_template = "admin/model/edit.html"
    """Default edit template"""

    create_template = "admin/model/create.html"
    """Default create template"""

    details_template = "admin/model/details.html"
    """Default details view template"""

    # Modal Templates
    edit_modal_template = "admin/model/modals/edit.html"
    """Default edit modal template"""

    create_modal_template = "admin/model/modals/create.html"
    """Default create modal template"""

    details_modal_template = "admin/model/modals/details.html"
    """Default details modal view template"""

    # Modals
    edit_modal = False
    """Setting this to true will display the edit_view as a modal dialog."""

    create_modal = False
    """Setting this to true will display the create_view as a modal dialog."""

    details_modal = False
    """Setting this to true will display the details_view as a modal dialog."""

    # Customizations
    column_list: Optional[T_COLUMN_LIST] = None
    """
        Collection of the model field names for the list view.
        If set to `None`, will get them from the model.

        For example::

            class MyModelView(BaseModelView):
                column_list = ('name', 'last_name', 'email')

        SQLAlchemy model attributes can be used instead of strings::

            class MyModelView(BaseModelView):
                column_list = ('name', 'user.last_name')

        When using SQLAlchemy models, you can reference related columns like this::
            class MyModelView(BaseModelView):
                column_list = ('<relationship>.<related column name>',)
    """

    column_details_list = None
    """
        Collection of the field names included in the details view.
        If set to `None`, will get them from the model.
    """

    column_export_list = None
    """
        Collection of the field names included in the export.
        If set to `None`, will get them from the model.
    """

    column_formatters = dict()
    """
        Dictionary of list view column formatters.

        For example, if you want to show price multiplied by
        two, you can do something like this::

            class MyModelView(BaseModelView):
                column_formatters = dict(price=lambda v, m, p: m.price*2)

        The Callback function has the prototype::

            def formatter(view, model, name):
                # `view` is current administrative view
                # `model` is model instance
                # `name` is property name
                pass
    """

    column_formatters_export = None
    """
        Dictionary of list view column formatters to be used for export.
        Defaults to column_formatters when set to None.
    """

    column_formatters_detail = None
    """
        Dictionary of list view column formatters to be used for the detail view.
        Defaults to column_formatters when set to None.
    """

    column_type_formatters: Optional[T_FORMATTERS] = None
    """
        Dictionary of value type formatters to be used in the list view.

        By default, three types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``bool`` will be displayed as a checkmark if it is ``True``
        3. ``list`` will be joined using ', '

        If you don't like the default behavior and don't want any type formatters
        applied, just override this property with an empty dictionary::

            class MyModelView(BaseModelView):
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

            class MyModelView(BaseModelView):
                column_type_formatters = MY_DEFAULT_FORMATTERS

        Type formatters have lower priority than list column formatters.

        The callback function has following prototype::

            def type_formatter(view, value):
                # `view` is current administrative view
                # `value` value to format
                pass
    """

    column_type_formatters_export = None
    """
        Dictionary of value type formatters to be used in the export.

        By default, two types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``list`` will be joined using ', '

        Functions the same way as column_type_formatters.
    """

    column_type_formatters_detail = None
    """
        Dictionary of value type formatters to be used in the detail view.

        By default, two types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``list`` will be joined using ', '

        Functions the same way as column_type_formatters.
    """

    column_labels = {}
    """
        Dictionary where key is column name and value is string to display.

        For example::

            class MyModelView(BaseModelView):
                column_labels = dict(name='Name', last_name='Last Name')
    """

    column_descriptions = None
    """
        Dictionary where key is column name and
        value is description for `list view` column or add/edit form field.

        For example::

            class MyModelView(BaseModelView):
                column_descriptions = dict(
                    full_name='First and Last name'
                )
    """

    column_sortable_list: Optional[T_COLUMN_LIST] = None
    """
        Collection of the sortable columns for the list view.
        If set to `None`, will get them from the model.

        For example::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', 'last_name')

        If you want to explicitly specify field/column to be used while
        sorting, you can use a tuple::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', ('user', 'user.username'))

        You can also specify multiple fields to be used while sorting::

            class MyModelView(BaseModelView):
                column_sortable_list = (
                    'name', ('user', ('user.first_name', 'user.last_name')))
        When using SQLAlchemy models, model attributes can be used instead
        of strings::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', ('user', 'user.username'))
    """

    column_default_sort = None
    """
        Default sort column if no sorting is applied.

        Example::

            class MyModelView(BaseModelView):
                column_default_sort = 'user'

        You can use tuple to control ascending descending order. In following example, items
        will be sorted in descending order::

            class MyModelView(BaseModelView):
                column_default_sort = ('user', True)

        If you want to sort by more than one column,
        you can pass a list of tuples::

            class MyModelView(BaseModelView):
                column_default_sort = [('name', True), ('last_name', True)]
    """

    column_searchable_list: Optional[T_COLUMN_LIST] = None
    """
        A collection of the searchable columns. It is assumed that only
        text-only fields are searchable, but it is up to the model
        implementation to decide.

        Example::

            class MyModelView(BaseModelView):
                column_searchable_list = ('name', 'email')
    """

    column_editable_list = None
    """
        Collection of the columns which can be edited from the list view.

        For example::

            class MyModelView(BaseModelView):
                column_editable_list = ('name', 'last_name')
    """

    column_choices = {}
    """
        Map choices to columns in list view

        Example::

            class MyModelView(BaseModelView):
                column_choices = {
                    'my_column': {
                        'db_value': 'display_value',
                        'db_value2': 'display_value2',
                    }
                }
    """

    form_args = None
    """
        Dictionary of form field arguments. Refer to WTForms documentation for
        list of possible options.

        Example::

            from wtforms.validators import DataRequired
            class MyModelView(BaseModelView):
                form_args = dict(
                    name=dict(label='First Name', validators=[DataRequired()])
                )
    """

    form_columns = None
    """
        Collection of the model field names for the form. If set to `None` will
        get them from the model.

        Example::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'email')

        SQLAlchemy model attributes can be used instead of strings::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'user.last_name')
    """

    form_excluded_columns = None
    """
        Collection of excluded form field names.

        For example::

            class MyModelView(BaseModelView):
                form_excluded_columns = ('last_name', 'email')
    """

    form_widget_args = None
    """
        Dictionary of form widget rendering arguments.
        Use this to customize how widget is rendered without using custom template.

        Example::

            class MyModelView(BaseModelView):
                form_widget_args = {
                    'description': {
                        'rows': 10,
                        'style': 'color: black'
                    },
                    'other_field': {
                        'disabled': True
                    }
                }

        Changing the format of a DateTimeField will require changes to both form_widget_args and form_args.

        Example::

            form_args = dict(
                start=dict(format='%Y-%m-%d %I:%M %p') # changes how the input is parsed by strptime (12 hour time)
            )
            form_widget_args = dict(
                start={
                    'data-date-format': u'yyyy-mm-dd HH:ii P',
                    'data-show-meridian': 'True'
                } # changes how the DateTimeField displays the time
            )
    """

    form_extra_fields = None
    """
        Dictionary of additional fields.

        Example::

            class MyModelView(BaseModelView):
                form_extra_fields = {
                    'password': PasswordField('Password')
                }

        You can control order of form fields using ``form_columns`` property. For example::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'email', 'password', 'secret')

                form_extra_fields = {
                    'password': PasswordField('Password')
                }

        In this case, password field will be put between email and secret fields that are autogenerated.
    """

    form_ajax_refs = None
    """
        Use AJAX for foreign key model loading.

        Should contain dictionary, where key is field name and value is either a dictionary which
        configures AJAX lookups or backend-specific `AjaxModelLoader` class instance.

        For example, it can look like::

            class MyModelView(BaseModelView):
                form_ajax_refs = {
                    'user': {
                        'fields': ('first_name', 'last_name', 'email'),
                        'placeholder': 'Please select',
                        'page_size': 10,
                        'minimum_input_length': 0,
                    }
                }

        Or with SQLAlchemy backend like this::

            class MyModelView(BaseModelView):
                form_ajax_refs = {
                    'user': QueryAjaxModelLoader('user', User, self.session, fields=['email'], page_size=10)
                }

        If you need custom loading functionality, you can implement your custom loading behavior
        in your `AjaxModelLoader` class.
    """

    # Export settings
    export_max_rows = 0
    """
        Maximum number of rows allowed for export.

        Unlimited by default. Uses `page_size` if set to `None`.
    """

    export_types = ["csv"]
    """
        A list of available export filetypes. `csv` only is default, but any
        filetypes supported by tablib can be used.

        Check tablib for https://tablib.readthedocs.io/en/stable/formats.html
        for supported types.
    """

    # Pagination settings
    page_size = 20
    """
        Default page size for pagination.
    """

    can_set_page_size = False
    """
        Allows to select page size via dropdown list
    """

    page_size_options: tuple = (20, 50, 100)
    """
        Sets the page size options available, if `can_set_page_size` is True
    """

    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        static_folder=None,
    ):
        """
        Constructor.

        :param model:
            Model class
        :param name:
            View name. If not provided, will use the model class name
        :param endpoint:
            Base endpoint. If not provided, will use the model name.
        :param url:
            Base URL. If not provided, will use endpoint as a URL.
        """
        self.model = model

        if name is None:
            name = self._prettify_class_name(model.__name__)

        if endpoint is None:
            endpoint = self.model.__name__.lower()

        super().__init__(
            name,
            endpoint,
            url,
            static_folder,
        )

        self._init_view()

    def _init_view(self):
        # ActionMixin
        self.init_actions()

        # RowActionMixin
        self.init_row_actions()

        #
        self._list_columns = self.get_list_columns()
        self._sortable_columns = self.get_sortable_columns()
        self._details_columns = self.get_details_columns()
        self._export_columns = self.get_export_columns()

        # Forms
        self._init_forms()

        # Search
        self._search_supported = self.init_search()

        # Filters
        self.init_filters()

        # Column formatters
        if self.column_formatters_export is None:
            self.column_formatters_export = self.column_formatters

        if self.column_formatters_detail is None:
            self.column_formatters_detail = self.column_formatters

        # Type formatters
        if self.column_type_formatters is None:
            self.column_type_formatters = dict(BASE_FORMATTERS)

        if self.column_type_formatters_export is None:
            self.column_type_formatters_export = dict(EXPORT_FORMATTERS)

        if self.column_type_formatters_detail is None:
            self.column_type_formatters_detail = dict(DETAIL_FORMATTERS)

        if self.column_descriptions is None:
            self.column_descriptions = dict()

    def _init_forms(self):
        self._form_ajax_refs = self._process_ajax_references()

        if self.form_widget_args is None:
            self.form_widget_args = {}

        self._create_form_class = self.get_create_form()
        self._edit_form_class = self.get_edit_form()
        self._delete_form_class = self.get_delete_form()

        # List View In-Line Editing
        if self.column_editable_list:
            self._list_form_class = self.get_list_form()
        else:
            self.column_editable_list = {}

    def get_pk_value(self, obj):
        """
        Return PK value from a model object.
        """
        raise NotImplementedError()

    def scaffold_list_columns(self):
        """
        Return list of the model field names. Must be implemented in the child class.

        Expected return format is list of strings of the field names. For example::

            ['name', 'first_name', 'last_name']
        """
        raise NotImplementedError("Please implement scaffold_list_columns method")

    def get_column_label(self, column_name):
        """
        Return a human-readable column name.

        :param column_name:
            Model field name.
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]
        else:
            return self._prettify_name(column_name)

    def get_column_names(self, columns):
        """
        Returns a list of tuples with the model field name and formatted
        field name.

        :param columns:
            List of columns to include in the results.
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self):
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_list`.
        If `column_list` is not set, the columns from `scaffold_list_columns` will be used.
        """
        return self.get_column_names(self.column_list or self.scaffold_list_columns())

    def get_details_columns(self):
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_details_list`.
        If `column_details_list` is not set, the columns from `scaffold_list_columns` will be used.
        """
        return self.get_column_names(
            self.column_details_list or self.scaffold_list_columns()
        )

    def get_export_columns(self):
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_export_list`.
        If `column_export_list` is not set, it will attempt to use the columns from `column_list`
        or finally the columns from `scaffold_list_columns` will be used.
        """
        return self.get_column_names(
            self.column_export_list or self.column_list or self.scaffold_list_columns()
        )

    def scaffold_sortable_columns(self):
        """
        Returns dictionary of sortable columns. Must be implemented in
        the child class.

        Expected return format is a dictionary, where keys are field names and
        values are property names.
        """
        raise NotImplementedError("Please implement scaffold_sortable_columns method")

    def get_sortable_columns(self):
        """
        Returns a dictionary of the sortable columns. Key is a model
        field name and value is sort column (for example - attribute).

        If `column_sortable_list` is set, will use it. Otherwise, will call
        `scaffold_sortable_columns` to get them from the model.
        """
        if self.column_sortable_list is None:
            return self.scaffold_sortable_columns() or dict()
        else:
            result = dict()

            for c in self.column_sortable_list:
                if isinstance(c, tuple):
                    result[c[0]] = c[1]
                else:
                    result[c] = c

            return result

    def init_search(self):
        """
        Initialize search. If data provider does not support search,
        `init_search` will return `False`.
        """
        return False

    def search_placeholder(self):
        """
        Return search placeholder text.
        """
        return None

    # Form helpers
    def scaffold_form(self):
        """
        Create `form.BaseForm` inherited class from the model. Must be
        implemented in the child class.
        """
        raise NotImplementedError("Please implement scaffold_form method")

    def scaffold_list_form(self, widget=None, validators=None):
        """
        Create form for the `index_view` using only the columns from
        `self.column_editable_list`.

        :param widget:
            WTForms widget class. Defaults to `XEditableWidget`.
        :param validators:
            `form_args` dict with only validators
            {'name': {'validators': [DataRequired()]}}

        Must be implemented in the child class.
        """
        raise NotImplementedError("Please implement scaffold_list_form method")

    def get_list_form(self):
        """
        Get form class for the editable list view.

        Uses only validators from `form_args` to build the form class.

        Allows overriding the editable list view field/widget. For example::

            from .model.widgets import XEditableWidget

            class CustomWidget(XEditableWidget):
                def get_kwargs(self, subfield, kwargs):
                    if subfield.type == 'TextAreaField':
                        kwargs['data-type'] = 'textarea'
                        kwargs['data-rows'] = '20'
                    # elif: kwargs for other fields

                    return kwargs

            class MyModelView(BaseModelView):
                def get_list_form(self):
                    return self.scaffold_list_form(widget=CustomWidget)
        """
        if self.form_args:
            # get only validators, other form_args can break FieldList wrapper
            validators = dict(
                (key, {"validators": value["validators"]})
                for key, value in self.form_args.items()
                if value.get("validators")
            )
        else:
            validators = None

        return self.scaffold_list_form(validators=validators)

    def get_create_form(self):
        """
        Create form class for model creation view.

        Override to implement customized behavior.
        """
        return self.scaffold_form()

    def get_edit_form(self):
        """
        Create form class for model editing view.

        Override to implement customized behavior.
        """
        return self.scaffold_form()

    def get_delete_form(self):
        """
        Create form class for model delete view.

        Override to implement customized behavior.
        """

        class DeleteForm(self.form_base_class):
            id = HiddenField(validators=[InputRequired()])

        return DeleteForm

    def create_form(self, *args, **kwargs):
        """
        Instantiate model creation form and return it.

        Override to implement custom behavior.
        """
        return self._create_form_class(*args, **kwargs)

    def edit_form(self, *args, **kwargs):
        """
        Instantiate model editing form and return it.

        Override to implement custom behavior.
        """
        return self._edit_form_class(*args, **kwargs)

    def delete_form(self, *args, **kwargs):
        """
        Instantiate model delete form and return it.

        Override to implement custom behavior.
        """
        return self._delete_form_class(*args, **kwargs)

    def list_form(self, *args, **kwargs):
        """
        Instantiate model editing form for list view and return it.

        Override to implement custom behavior.
        """
        return self._list_form_class(*args, **kwargs)

    def get_save_return_url(self, model, is_created=False):
        """
        Return url where user is redirected after successful form save.

        :param model:
            Saved object
        :param is_created:
            Whether new object was created or existing one was updated

        For example, redirect use to object details view after form save::

            class MyModelView(ModelView):
                def get_save_return_url(self, model, is_created):
                    return self.get_url('.details_view', id=model.id)

        """
        return self.get_url(".details_view", id=model.id)

    # Helpers
    def is_sortable(self, name):
        """
        Verify if column is sortable.

        Not case-sensitive.

        :param name:
            Column name.
        """
        return name.lower() in (x.lower() for x in self._sortable_columns)

    def is_editable(self, name):
        """
        Verify if column is editable.

        :param name:
            Column name.
        """
        return name in self.column_editable_list and self.can_edit

    def _get_column_by_idx(self, idx):
        """
        Return column index by
        """
        if idx is None or idx < 0 or idx >= len(self._list_columns):
            return None

        return self._list_columns[idx]

    def _get_default_order(self):
        """
        Return default sort order
        """
        if self.column_default_sort:
            if isinstance(self.column_default_sort, list):
                return self.column_default_sort
            if isinstance(self.column_default_sort, tuple):
                return [self.column_default_sort]
            else:
                return [(self.column_default_sort, False)]

        return None

    def get_safe_page_size(self, page_size):
        safe_page_size = self.page_size

        if self.can_set_page_size and page_size in self.page_size_options:
            safe_page_size = page_size

        return safe_page_size

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        """
        Return a tuple of a count of results and a paginated and sorted list of models from the data source.

        Must be implemented in the child class.

        :param page:
            Page number, 0 based. Can be set to None if it is first page.
        :param sort_field:
            Sort column name or None.
        :param sort_desc:
            If set to True, sorting is in descending order.
        :param search:
            Search query
        :param filters:
            List of filter tuples. First value in a tuple is a search
            index, second value is a search value.
        :param page_size:
            Number of results. Defaults to ModelView's page_size. Can be
            overriden to change the page_size limit. Removing the page_size
            limit requires setting page_size to 0 or False.
        """
        raise NotImplementedError("Please implement get_list method")

    def get_one(self, id):
        """
        Return one model by its id.

        Must be implemented in the child class.

        :param id:
            Model id
        """
        raise NotImplementedError("Please implement get_one method")

    def create_model(self, form):
        """
        Create model from the form.

        Returns the model instance if operation succeeded.

        Must be implemented in the child class.

        :param form:
            Form instance
        """
        raise NotImplementedError()

    def update_model(self, form, model):
        """
        Update model from the form.

        Returns `True` if operation succeeded.

        Must be implemented in the child class.

        :param form:
            Form instance
        :param model:
            Model instance
        """
        raise NotImplementedError()

    def delete_model(self, model):
        """
        Delete model.

        Returns `True` if operation succeeded.

        Must be implemented in the child class.

        :param model:
            Model instance
        """
        raise NotImplementedError()

    def _get_list_extra_args(self):
        """
        Return arguments from query string.
        """
        return ViewArgs(
            page=request.args.get("page", 0, type=int),
            page_size=request.args.get("page_size", 0, type=int),
            sort=request.args.get("sort", None, type=int),
            sort_desc=request.args.get("desc", None, type=int),
            search=request.args.get("search", None),
            filters=self._get_list_filter_args(),
            extra_args=dict(
                [
                    (k, v)
                    for k, v in request.args.items()
                    if k
                    not in (
                        "page",
                        "page_size",
                        "sort",
                        "desc",
                        "search",
                    )
                    and not k.startswith("flt")
                ]
            ),
        )

    # URL generation helpers
    def _get_list_url(self, view_args):
        """
        Generate page URL with current page, sort column and
        other parameters.

        :param view:
            View name
        :param view_args:
            ViewArgs object with page number, filters, etc.
        """
        page = view_args.page or None
        desc = 1 if view_args.sort_desc else None

        kwargs = dict(
            page=page, sort=view_args.sort, desc=desc, search=view_args.search
        )
        kwargs.update(view_args.extra_args)

        kwargs["page_size"] = self.get_safe_page_size(view_args.page_size)

        kwargs.update(self._get_filters(view_args.filters))

        return self.get_url(".index_view", **kwargs)

    def _get_object_attr(self, obj, name):
        """
        Recursive getattr from the obj by the name. Name can be a dot-delimited string to get nested attributes.

        :param name:
            Dot delimited attribute name, for example 'user.username' to get obj.user.username.
        """
        return reduce(getattr, name.split("."), obj)

    def _get_format_value(self, model, name, column_formatters, column_type_formatters):
        """
        Returns the value to be displayed.

        :param model:
            Model instance
        :param name:
            Field name
        :param column_formatters:
            column_formatters to be used.
        :param column_type_formatters:
            column_type_formatters to be used.
        """
        column_fmt = column_formatters.get(name)
        if column_fmt is not None:
            value = column_fmt(self, model, name)
        else:
            value = self._get_object_attr(model, name)

        choices_map = self.column_choices.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        type_fmt = None
        for typeobj, formatter in column_type_formatters.items():
            if isinstance(value, typeobj):
                type_fmt = formatter
                break
        if type_fmt is not None:
            value = type_fmt(self, value, name)

        return value

    def get_list_value(self, model, name):
        """
        Returns the value to be displayed in the list view

        :param model:
            Model instance
        :param name:
            Field name
        """
        return self._get_format_value(
            model,
            name,
            self.column_formatters,
            self.column_type_formatters,
        )

    def get_detail_value(self, model, name):
        """
        Returns the value to be displayed in the detail view

        :param model:
            Model instance
        :param name:
            Field name
        """
        return self._get_format_value(
            model,
            name,
            self.column_formatters_detail,
            self.column_type_formatters_detail,
        )

    def get_export_value(self, model, name):
        """
        Returns the value to be displayed in export.
        Allows export to use different (non HTML) formatters.

        :param model:
            Model instance
        :param name:
            Field name
        """
        return self._get_format_value(
            model,
            name,
            self.column_formatters_export,
            self.column_type_formatters_export,
        )

    def get_export_name(self, export_type="csv"):
        """
        :return: The exported csv file name.
        """
        filename = "%s_%s.%s" % (
            self.name,
            time.strftime("%Y-%m-%d_%H-%M-%S"),
            export_type,
        )
        return filename

    # AJAX references
    def _process_ajax_references(self):
        """
        Process `form_ajax_refs` and generate model loaders that
        will be used by the `ajax_lookup` view.
        """
        result = {}

        if self.form_ajax_refs:
            for name, options in self.form_ajax_refs.items():
                if isinstance(options, dict):
                    result[name] = self._create_ajax_loader(name, options)
                elif isinstance(options, AjaxModelLoader):
                    result[name] = options
                else:
                    raise ValueError(
                        "%s.form_ajax_refs can not handle %s types"
                        % (self, type(options))
                    )

        return result

    def _create_ajax_loader(self, name, options):
        """
        Model backend will override this to implement AJAX model loading.
        """
        raise NotImplementedError()

    def get_redirect_target(self, param_name="url", endpoint=".index_view"):
        return request.values.get(param_name) or self.get_url(endpoint)

    def is_action_allowed(self, name):
        if name == "delete" and not self.can_delete:
            return False
        return super().is_action_allowed(name)

    @expose_url("/")
    def index_view(self):
        if self.can_delete:
            delete_form = self.delete_form()
        else:
            delete_form = None

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get page size
        page_size = self.get_safe_page_size(view_args.page_size)

        # Get count and data
        count, data = self.get_list(
            view_args.page,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=page_size,
        )

        # Calculate number of pages
        if count is not None and page_size:
            num_pages = int(ceil(count / float(page_size)))
        elif not page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1

            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def page_size_url(s):
            return self._get_list_url(view_args.clone(page_size=s))

        clear_search_url = self._get_list_url(
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
            # List
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            can_set_page_size=self.can_set_page_size,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            default_page_size=self.page_size,
            # Sorting
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,
            # Search
            search_supported=self._search_supported,
            clear_search_url=clear_search_url,
            search=view_args.search,
            search_placeholder=self.search_placeholder(),
            # Filters
            filters=self._filters,
            filter_groups=self._get_filter_groups(),
            active_filters=view_args.filters,
            filter_args=self._get_filters(view_args.filters),
            # Misc
            return_url=self._get_list_url(view_args),
            # Extras
            extra_args=view_args.extra_args,
        )

    @expose_url("/new/", methods=("GET", "POST"))
    def create_view(self):
        """
        Create model view
        """
        return_url = self.get_redirect_target()

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()

        if form.validate_on_submit():
            model = self.create_model(form)
            if model:
                flash(gettext("Record was successfully created."), "success")
                if "_add_another" in request.form:
                    return redirect(request.url)
                elif "_continue_editing" in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url(
                            ".edit_view", id=self.get_pk_value(model), url=return_url
                        )
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.create_modal and request.args.get("modal"):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(
            template, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        """
        Edit model view
        """
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

        form = self._edit_form_class(obj=model)

        if form.validate_on_submit():
            if self.update_model(form, model):
                flash(gettext("Record was successfully saved."), "success")
                if "_add_another" in request.form:
                    return redirect(self.get_url(".create_view", url=return_url))
                elif "_continue_editing" in request.form:
                    return redirect(
                        self.get_url(".edit_view", id=self.get_pk_value(model))
                    )
                else:
                    return redirect(self.get_save_return_url(model, is_created=False))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.edit_modal and request.args.get("modal"):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(
            template, model=model, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/details/")
    def details_view(self):
        """
        Details model view
        """
        return_url = self.get_redirect_target()

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        if self.details_modal and request.args.get("modal"):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(
            template,
            model=model,
            details_columns=self._details_columns,
            return_url=return_url,
        )

    @expose_url("/delete/", methods=("POST",))
    def delete_view(self):
        """
        Delete model view. Only POST method is allowed.
        """
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
            form.flash_errors(message="Failed to delete record. %(error)s")
        return redirect(return_url)

    def _export_data(self):
        # Macros in column_formatters are not supported.
        # Macros will have a function name 'inner'
        # This causes non-macro functions named 'inner' not work.
        for col, func in self.column_formatters_export.items():
            # skip checking columns not being exported
            if col not in [col for col, _ in self._export_columns]:
                continue

            if func.__name__ == "inner":
                raise NotImplementedError(
                    "Macros are not implemented in export. Exclude column in"
                    " column_formatters_export, column_export_list "
                    ". Column: %s" % (col,)
                )

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get count and data
        count, data = self.get_list(
            0,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=self.export_max_rows,
        )

        return count, data

    @expose_url("/export/<export_type>/")
    def export(self, export_type):
        return_url = self.get_redirect_target()

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext("Permission denied."), "error")
            return redirect(return_url)

        if export_type == "csv":
            return self._export_csv(return_url)
        else:
            return self._export_tablib(export_type, return_url)

    def _export_csv(self, return_url):
        """
        Export a CSV of records as a stream.
        """
        count, data = self._export_data()

        # https://docs.djangoproject.com/en/1.8/howto/outputting-csv/
        class Echo:
            """
            An object that implements just the write method of the file-like
            interface.
            """

            def write(self, value):
                """
                Write the value by returning it, instead of storing
                in a buffer.
                """
                return value

        writer = csv.writer(Echo())

        def generate():
            # Append the column titles at the beginning
            titles = [c[1] for c in self._export_columns]
            yield writer.writerow(titles)

            for row in data:
                vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
                yield writer.writerow(vals)

        filename = self.get_export_name(export_type="csv")

        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        return Response(
            stream_with_context(generate()),
            headers={"Content-Disposition": disposition},
            mimetype="text/csv",
        )

    def _export_tablib(self, export_type, return_url):
        """
        Exports a variety of formats using the tablib library.
        """

        filename = self.get_export_name(export_type)

        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if encoding:
            mimetype = "%s; charset=%s" % (mimetype, encoding)

        ds = tablib.Dataset(headers=[c[1] for c in self._export_columns])

        count, data = self._export_data()

        for row in data:
            vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
            ds.append(vals)

        try:
            try:
                response_data = ds.export(format=export_type)
            except AttributeError:
                response_data = getattr(ds, export_type)
        except (AttributeError, tablib.UnsupportedFormat):
            flash(
                gettext('Export type "%(type)s not supported.', type=export_type),
                "error",
            )
            return redirect(return_url)

        return Response(
            response_data,
            headers={"Content-Disposition": disposition},
            mimetype=mimetype,
        )

    @expose_url("/ajax/lookup/")
    def ajax_lookup(self):
        name = request.args.get("name")
        query = request.args.get("query")
        offset = request.args.get("offset", type=int)
        limit = request.args.get("limit", 10, type=int)
        loader = self._form_ajax_refs.get(name)
        if not loader:
            abort(404)

        data = [loader.format(m) for m in loader.get_list(query, offset, limit)]
        return jsonify(data)

    @expose_url("/ajax/update/", methods=("POST",))
    def ajax_update(self):
        """
        Edits a single column of a record in list view.
        """
        if not self.column_editable_list:
            abort(404)

        form = self.list_form()

        # prevent validation issues due to submitting a single field
        # delete all fields except the submitted fields and csrf token
        for field in list(form):
            if (field.name in request.form) or (field.name == "csrf_token"):
                pass
            else:
                form.__delitem__(field.name)
        if form.validate_on_submit():
            pk = form.list_form_pk.data
            record = self.get_one(pk)

            if record is None:
                return gettext("Record does not exist."), 500

            if self.update_model(form, record):
                # Success
                return gettext("Record was successfully saved.")
            else:
                # Error: No records changed, or problem saving to database.
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
                            gettext("Failed to update record. %(error)s", error=error),
                            500,
                        )
