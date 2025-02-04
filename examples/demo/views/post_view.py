from markupsafe import Markup
from wtforms import validators
from flask_babel import gettext
from flask_exts.admin.sqla import ModelView
from flask_exts.admin.sqla.filters import BaseSQLAFilter
from flask_exts.admin.sqla.filters import FilterEqual
from flask_exts.admin.sqla.filters import FilterLike
from ..models import db
from ..models.post import AVAILABLE_USER_TYPES, Author, Post, Tag


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
        "posts",
        "website",
        "enum_choice_field",
    ] + column_list
    form_columns = [
        "id",
        "type",
        "posts",
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
        form.posts.query_factory = lambda: Post.query.filter(
            Post.author_id == form._obj.id
        ).all()
        return form


# Customized Post model admin
class PostView(ModelView):
    column_display_pk = True
    column_list = [
        "id",
        "author",
        "title",
        "date",
        "tags",
        "color",
        "created_at",
    ]
    column_editable_list = [
        "color",
    ]
    column_default_sort = ("date", True)
    create_modal = True
    edit_modal = True
    column_sortable_list = [
        "id",
        "title",
        "date",
        (
            "author",
            ("author.last_name", "author.first_name"),
        ),  # sort on multiple columns
    ]
    column_labels = {"title": "Post Title"}  # Rename 'title' column in list view
    column_searchable_list = [
        "title",
        "tags.name",
        "author.first_name",
        "author.last_name",
    ]
    column_labels = {
        "title": "Title",
        "tags.name": "Tags",
        "author.first_name": "Author's first name",
        "author.last_name": "Last name",
    }
    column_filters = [
        "id",
        "author.first_name",
        "author.id",
        "color",
        "created_at",
        "title",
        "date",
        "tags",
        FilterLike(
            Post.title,
            "Fixed Title",
            options=(("test1", "Test 1"), ("test2", "Test 2")),
        ),
    ]
    can_export = True
    export_max_rows = 1000
    export_types = ["csv", "xls"]

    # Pass arguments to WTForms. In this case, change label for text field to
    # be 'Big Text' and add DataRequired() validator.
    form_args = {"text": dict(label="Big Text", validators=[validators.DataRequired()])}
    form_widget_args = {"text": {"rows": 10}}

    form_ajax_refs = {
        "author": {"fields": (Author.first_name, Author.last_name)},
        "tags": {
            "fields": (Tag.name,),
            "minimum_input_length": 0,  # show suggestions, even before any author input
            "placeholder": "Please select",
            "page_size": 5,
        },
    }



# Add views
authorview = AuthorView(Author, db.session)
tagview = ModelView(Tag, db.session)
postview = PostView(Post, db.session)
