from wtforms import validators
from flask_exts.admin.sqla import ModelView
from flask_exts.admin.sqla.filters import FilterLike
from ..models.post import Post
from ..models.author import Author


# Customized Post model admin
class PostView(ModelView):
    can_view_details = True
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
        # "tags": {
        #     "fields": (Tag.name,),
        #     "minimum_input_length": 0,  # show suggestions, even before any author input
        #     "placeholder": "Please select",
        #     "page_size": 5,
        # },
    }

    column_descriptions = dict(
        color='favorite color'
        )


# Add views


postview = PostView(Post)
