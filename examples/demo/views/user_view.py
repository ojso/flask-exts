from flask_exts.admin.sqla.view import SqlaModelView
from ..models.user import MyUser


class UserView(SqlaModelView):
    # column_list = ("id", "username", "keywords", "keywords_values")
    column_list = ("id", "username")
    column_sortable_list = ("id", "username")
    # column_filters = ("id", "username", "keywords")
    column_filters = ("id", "username")
    # form_columns = ("username", "keywords")
    form_columns = ("username",)
    can_view_details = True


userview = UserView(MyUser, name="Users", endpoint="users")
