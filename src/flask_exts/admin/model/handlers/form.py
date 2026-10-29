from wtforms.fields import HiddenField
from wtforms.fields.core import UnboundField
from wtforms.validators import InputRequired

from ....forms.widgets import EditableWidget


class FormHandler:
    """Handler for form scaffolding and management in admin views."""

    def __init__(self, view):
        self.view = view
        self.base_form_class = self.view.base_form_class
        self.init_forms()

    def init_forms(self):
        # delete form
        class DeleteForm(self.base_form_class):
            id = HiddenField(validators=[InputRequired()])

        self._delete_form_class = DeleteForm
        self._create_form_class = self.view.scaffold_form("create")
        self._edit_form_class = self.view.scaffold_form("edit")

        # list edit form
        self._list_form_class = None
        if self.view.column_editable_list:
            if self.view.form_args:
                validators = {
                    key: {"validators": value["validators"]}
                    for key, value in self.view.form_args.items()
                    if value.get("validators")
                }
            else:
                validators = None

            self._list_form_class = self.create_editable_list_form(
                self.view.scaffold_list_form(validators=validators)
            )

    def create_editable_list_form(self, form_class, widget=None):
        """Create a form class with all the fields wrapped in a FieldList.

        Args:
            form_class: WTForms form class.
            widget: WTForms widget class. Defaults to `EditableWidget`.
        """
        if widget is None:
            widget = EditableWidget()

        class ListForm(self.base_form_class):
            pk = HiddenField(validators=[InputRequired()])

        for name, obj in form_class.__dict__.items():
            if not name.startswith("_") and isinstance(obj, UnboundField):
                if name == "pk":
                    raise ValueError("Form already has a pk column.")
                obj.kwargs["widget"] = widget
                setattr(ListForm, name, obj)

        return ListForm

    def create_form(self, *args, **kwargs):
        """Instantiate the form used by the create view.

        Args:
            *args: Positional arguments forwarded to the form.
            **kwargs: Keyword arguments forwarded to the form.

        Returns:
            A form instance.
        """
        return self._create_form_class(*args, **kwargs)

    def edit_form(self, *args, **kwargs):
        """Instantiate the form used by the edit view.

        Args:
            *args: Positional arguments forwarded to the form.
            **kwargs: Keyword arguments forwarded to the form.

        Returns:
            A form instance.
        """
        return self._edit_form_class(*args, **kwargs)

    def delete_form(self, *args, **kwargs):
        """Instantiate the form used by the delete view.

        Args:
            *args: Positional arguments forwarded to the form.
            **kwargs: Keyword arguments forwarded to the form.

        Returns:
            A form instance.
        """
        return self._delete_form_class(*args, **kwargs)

    def list_form(self, *args, **kwargs):
        """Instantiate and return the list-edit form for the index view.

        Args:
            *args: Positional arguments forwarded to the form.
            **kwargs: Keyword arguments forwarded to the form.

        Returns:
            A form instance.
        """

        return self._list_form_class(*args, **kwargs)
