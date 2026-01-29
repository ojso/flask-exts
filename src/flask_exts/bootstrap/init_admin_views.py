from ..views.index.view import IndexView
from ..views.user.view import UserView

def add_views(app):
    admin = app.extensions["exts"].admin
    admin.add_view(IndexView(), is_menu=False)
    admin.add_view(UserView(), is_menu=False)
    