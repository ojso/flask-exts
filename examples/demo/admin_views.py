from .views.author_view import authorview
from .views.post_view import postview
from .views.tag_view import tagview
from .views.tree_view import treeview


def register_views(app):
    admin = app.extensions["exts"].get_extension("admin").get_admin()
    admin.register_view(authorview)
    admin.register_view(postview)
    admin.register_view(tagview)    
    admin.register_view(treeview)
