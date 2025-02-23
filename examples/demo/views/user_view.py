from flask_exts.admin.sqla import ModelView
from ..models import db
from ..models.user import User


class UserView(ModelView):
    column_list = ("id", "username", "keywords", "keywords_values")
    column_sortable_list = ("id", "username")
    column_filters = ("id", "username", "keywords")
    form_columns = ("username", "keywords")
    can_view_details = True


userview = UserView(User, endpoint="users")
