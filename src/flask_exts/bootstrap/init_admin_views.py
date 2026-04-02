from .index_view import IndexView
from ..usercenter.user_view import UserView

def add_views(app):
    admin = app.extensions["exts"].admin
    admin.add_view(IndexView(), is_menu=False)
    admin.add_view(UserView(), is_menu=False)
    