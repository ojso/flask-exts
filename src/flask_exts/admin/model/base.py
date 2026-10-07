from ..view import View
from .actions_mixin import ActionsMixin
from .core import (
    ColumnsMixin,
    FormsMixin,
    PaginationMixin,
    SortingMixin,
    ValuesMixin,
)
from .filter_mixin import FilterMixin
from .operations import (
    CreateOperationsMixin,
    DeleteOperationsMixin,
    ExportOperationsMixin,
    ReadOperationsMixin,
    UpdateOperationsMixin,
)
from .row_actions import RowActionMixin
from .types import T_COLUMN_LIST, T_FORMATTERS


class BaseModelView(
    View,
    ColumnsMixin,
    SortingMixin,
    PaginationMixin,
    ValuesMixin,
    FormsMixin,
    ReadOperationsMixin,
    CreateOperationsMixin,
    UpdateOperationsMixin,
    DeleteOperationsMixin,
    ExportOperationsMixin,
    ActionsMixin,
    RowActionMixin,
    FilterMixin,
):
    """Abstract base class for model-backed admin views.

    Concrete backend implementations should inherit from this class and provide
    the abstract methods required by the underlying admin layer.

    Required hooks include:

    - scaffold_list_columns(): return the list of model columns.
    - scaffold_sortable_columns(): return the sortable column mapping.
    - scaffold_form(): build a form class from the model.
    - scaffold_list_form(): build a list-edit form from the model.
    - get_list(): fetch paginated data from the model.
    - get_one(): fetch one model by id.
    - get_pk_value(): read the primary key value from a model.
    - create_model(): create a new model from a form.
    - update_model(): update an existing model from a form.
    - delete_model(): delete a model.
    - _create_ajax_loader(): create an AJAX loader when form_ajax_refs is used.

    Example:
        ```python
        from flask_exts.admin.model import ModelView

        class UserAdmin(ModelView):
            column_list = ['id', 'username', 'email', 'created_at']
            column_sortable_list = ['username', 'created_at']
            form_columns = ['username', 'email', 'password']

            def scaffold_list_columns(self):
                return ['id', 'username', 'email', 'created_at']

            def scaffold_sortable_columns(self):
                return {'username': 'username', 'created_at': 'created_at'}

            def scaffold_form(self):
                return generate_form_from_model(User)

            def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
                query = User.query
                return count, items
        ```

    The class combines column management, filtering, sorting, pagination,
    formatting, forms, CRUD operations, and export support.
    """

    # Permissions
    can_create = True
    """Is model creation allowed"""

    can_edit = True
    """Is model editing allowed"""

    can_delete = True
    """Is model deletion allowed"""

    # Templates
    list_template = "admin/model/list.html"
    """Default list view template"""

    edit_template = "admin/model/edit.html"
    """Default edit template"""

    create_template = "admin/model/create.html"
    """Default create template"""

    details_template = "admin/model/details.html"
    """Default details view template"""

    column_formatters = {}
    """
        Dictionary of list view column formatters.

        For example, if you want to show price multiplied by
        two, you can do something like this::

            class MyModelView(BaseModelView):
                column_formatters = {"price": lambda v, m, p: m.price*2}

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

    column_type_formatters: T_FORMATTERS | None = None
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
                column_labels = {"name": "Name", "last_name": "Last Name"}
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

    column_sortable_list: T_COLUMN_LIST | None = None
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

    column_searchable_list: T_COLUMN_LIST | None = None
    """
        A collection of the searchable columns. It is assumed that only
        text-only fields are searchable, but it is up to the model
        implementation to decide.

        Example::

            class MyModelView(ModelView):
                column_searchable_list = ('name', 'email')

        You can also pass relation.column::

            class MyModelView(ModelView):
                column_searchable_list = (user.name, user.email)

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

    form_args = {}
    """
        Dictionary of form field arguments. Refer to WTForms documentation for
        list of possible options.

        Example::

            from wtforms.validators import DataRequired
            class MyModelView(BaseModelView):
                form_args = {
                    "name": {"label": "First Name", "validators": [DataRequired()]}
                }
    """

    form_columns = None
    """
        Collection of the model field names for the form. If set to `None` will
        get them from the model.

        Example::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'email')
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

            form_args = {
                "start": {"format": "%Y-%m-%d %I:%M %p"} # changes how the input is parsed by strptime (12 hour time)
            }
            form_widget_args = {
                "start": {
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
                    'user': AjaxSqlaModelLoader('user', User, self.session, fields=['email'], page_size=10)
                }
    """

