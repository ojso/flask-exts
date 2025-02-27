from .views.my_view import myview
from .views.user_view import userview
from .views.keyword_view import keywordview
from .views.tree_view import treeview
from .views.tag_view import tagview
from .views.author_view import authorview
from .views.post_view import postview
from flask_exts.admin.menu import MenuLink


def add_views(app):
    admin = app.extensions["admin"][0]

    admin.add_view(myview)
    admin.add_view(userview)
    admin.add_view(keywordview)
    admin.add_view(authorview)
    admin.add_view(tagview)
    admin.add_view(postview)
    admin.add_view(treeview)
    admin.menu.add_category(name="Links")
    admin.menu.add_link(MenuLink(name="Back Home", url="/", category="Links"))
    admin.menu.add_sub_category(name='External',parent_name='Links')
    # admin.menu.add_link(
    #     MenuLink(name="External link", url="http://www.example.com/", category="External")
    # )
