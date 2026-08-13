from .views.tree_view import treeview
from .views.tag_view import tagview
from .views.author_view import authorview
from .views.post_view import postview


def add_views(app):
    admin = app.extensions["exts"].admin
    admin.add_view(authorview)
    admin.add_view(postview)
    admin.add_view(tagview)    
    admin.add_view(treeview)
