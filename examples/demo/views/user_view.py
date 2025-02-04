from flask_exts.admin.sqla import ModelView
from ..models import db
from ..models.user import User


class UserView(ModelView):
    column_list = ("id", "username")
    column_sortable_list = ("id", "username")
    column_filters = ("id", "username")
    form_columns = ("username",)
    can_view_details = True


userview = UserView(User, db.session, endpoint="users")
