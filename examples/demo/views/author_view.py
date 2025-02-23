from markupsafe import Markup
from wtforms import validators
from flask_babel import gettext
from flask_exts.admin.sqla.filters import BaseSQLAFilter
from flask_exts.admin.sqla.filters import FilterEqual
from flask_exts.admin.sqla import ModelView
from ..models.author import Author, AVAILABLE_USER_TYPES
from ..models.post import Post


# Custom filter class
class FilterLastNameBrown(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        if value == "1":
            return query.filter(self.column == "Brown")
        else:
            return query.filter(self.column != "Brown")

    def operation(self):
        return "is Brown"


# Customized User model admin
def phone_number_formatter(view, context, model, name):
    return (
        Markup("<nobr>{}</nobr>".format(model.phone_number))
        if model.phone_number
        else None
    )


def is_numberic_validator(form, field):
    if field.data and not field.data.isdigit():
        raise validators.ValidationError(gettext("Only numbers are allowed."))


class AuthorView(ModelView):
    can_set_page_size = True
    page_size = 5
    page_size_options = (5, 10, 15)
    can_view_details = True  # show a modal dialog with records details
    action_disallowed_list = [
        "delete",
    ]

    form_choices = {
        "type": AVAILABLE_USER_TYPES,
    }
    form_args = {
        "dialling_code": {"label": "Dialling code"},
        "local_phone_number": {
            "label": "Phone number",
            "validators": [is_numberic_validator],
        },
    }
    form_widget_args = {"id": {"readonly": True}}
    column_list = [
        "type",
        "first_name",
        "last_name",
        "email",
        "ip_address",
        "currency",
        "timezone",
        "phone_number",
    ]
    column_searchable_list = [
        "first_name",
        "last_name",
        "phone_number",
        "email",
    ]
    column_editable_list = ["type", "currency", "timezone"]
    column_details_list = [
        "id",
        "featured_post",
        "website",
        "enum_choice_field",
    ] + column_list
    form_columns = [
        "id",
        "type",
        "featured_post",
        "enum_choice_field",
        "last_name",
        "first_name",
        "email",
        "website",
        "dialling_code",
        "local_phone_number",
    ]
    form_create_rules = [
        "last_name",
        "first_name",
        "type",
        "email",
    ]

    column_auto_select_related = True
    column_default_sort = [
        ("last_name", False),
        ("first_name", False),
    ]  # sort on multiple columns

    # custom filter: each filter in the list is a filter operation (equals, not equals, etc)
    # filters with the same name will appear as operations under the same filter
    column_filters = [
        "first_name",
        FilterEqual(column=Author.last_name, name="Last Name"),
        FilterLastNameBrown(
            column=Author.last_name,
            name="Last Name",
            options=(("1", "Yes"), ("0", "No")),
        ),
        "phone_number",
        "email",
        "ip_address",
        "currency",
        "timezone",
    ]
    column_formatters = {"phone_number": phone_number_formatter}

    # setup edit forms so that only posts created by this author can be selected as 'featured'
    def edit_form(self, obj):
        return self._filtered_posts(super().edit_form(obj))

    def _filtered_posts(self, form):
        form.featured_post.query_factory = lambda: Post.query.filter(
            Post.author_id == form.id._value()
        ).all()
        return form


authorview = AuthorView(Author)
