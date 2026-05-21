from wtforms import validators
from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.admin.sqla.filter import FilterLike
from flask_exts.admin.sqla.filter import BaseSQLAFilter
from flask_exts.admin.sqla.query import Query
from ..models.post import Post
from ..models.author import Author


# Custom filter class
class FilterNameBrown(BaseSQLAFilter):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, options=(("1", "Yes"), ("0", "No"))
        )

    def apply(self, query, value):
        if value == "1":
            return query.add_filter(self.column, "==", "Brown")
        else:
            return query.add_filter(self.column, "!=", "Brown")

    def operation(self):
        return "is Brown"


class PostView(SqlaModelView):
    column_list = [
        "id",
        "author",
        "author.email",
        "title",
        "date",
        "tags",
        "color",
        "created_at",
    ]
    column_labels = {
        "title": "Post Title",
        "tags.name": "TagsName",
        "author.first_name": "Author's first name",
        "author.last_name": "Last name",
    }

    column_editable_list = [
        "color",
    ]
    column_default_sort = ("date", True)
    # create_modal = True
    # edit_modal = True
    # details_modal = True

    column_sortable_list = [
        "id",
        "title",
        "date",
        (
            "author",
            ("author.last_name", "author.first_name"),
        ),  # sort on multiple columns
    ]
    column_searchable_list = [
        "title",
        "author.first_name",
        "author.last_name",
    ]

    column_filters = [
        "id",
        "author.first_name",
        "author.id",
        FilterNameBrown(
            column_type=Query.get_model_column_type(Author, "last_name"),
            column="author.last_name",
            name="Last Name",
        ),
        "color",
        "created_at",
        "title",
        "date",
        "tags.name",
        FilterLike(
            column_type=Query.get_model_column_type(Post, "title"),
            column="title",
            name="Fixed Title",
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
        "author": {"fields": ("first_name", "last_name")},
        # "tags": {
        #     "fields": ("name",),
        #     "minimum_input_length": 0,  # show suggestions, even before any author input
        #     "placeholder": "Please select",
        #     "page_size": 5,
        # },
    }

    column_descriptions = dict(color="favorite color")


postview = PostView(Post)
