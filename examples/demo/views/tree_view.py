from flask_exts.admin.sqla import ModelView
from ..models.tree import Tree


class TreeView(ModelView):
    list_template = "tree_list.html"
    column_auto_select_related = True
    column_list = [
        "id",
        "name",
        "parent",
    ]
    form_excluded_columns = [
        "children",
    ]
    column_filters = [
        "id",
        "name",
        "parent",
    ]

    # override the 'render' method to pass your own parameters to the template
    def render(self, template, **kwargs):
        return super().render(template, foo="bar", **kwargs)


treeview = TreeView(Tree)
