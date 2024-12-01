from flask import render_template
from flask import url_for
from .menu import MenuCategory, MenuView, MenuLink, SubMenuCategory
from .view import BaseView
from .views.index_view import IndexView
from .views.user_view import UserView


class Admin:
    """
    Collection of the admin views. Also manages menu structure.
    """

    def __init__(
        self,
        app=None,
        name="Admin",
        url="/admin",
        endpoint="admin",
        template_folder=None,
        static_folder=None,
        index_view=IndexView(),
        user_view=UserView(),
        category_icon_classes=None,
    ):
        """
        Constructor.

        :param app:
            Flask application object
        :param name:
            Application name. Will be displayed in the main menu and as a page title. Defaults to "Admin"
        :param url:
            Base URL
        :param subdomain:
            Subdomain to use
        :param index_view:
            Home page view to use. Defaults to `AdminIndexView`.
        :param translations_path:
            Location of the translation message catalogs. By default will use the translations
            shipped with Flask-Admin.
        :param endpoint:
            Base endpoint name for index view. If you use multiple instances of the `Admin` class with
            a single Flask application, you have to set a unique endpoint name for each instance.
        :param theme:
            Base theme. Defaults to `Bootstrap4Theme()`.
        :param category_icon_classes:
            A dict of category names as keys and html classes as values to be added to menu category icons.
            Example: {'Favorites': 'glyphicon glyphicon-star'}
        """
        self.app = app
        self.name = name
        self._views = []
        self._menu = []
        self._menu_categories = dict()
        self._menu_links = []
        self.endpoint = endpoint
        self.url = url
        if not self.url.startswith("/"):
            raise ValueError("admin.url must startswith /")
        self.template_folder = template_folder or "../templates"
        self.static_folder = static_folder or "../static"
        self.category_icon_classes = category_icon_classes or dict()

        self.index_view = index_view
        if self.index_view is not None:
            self.add_view(self.index_view, False)

        self.user_view = user_view
        if self.user_view is not None:
            self.add_view(self.user_view, False)

        # Register with application
        if app is not None:
            self._init_extension()

    def add_view(self, view, is_menu=True):
        """
        Add a view to the collection.

        :param view:
            View to add.
        """
        # attach self(admin) to view
        view.admin = self

        # Add to views
        self._views.append(view)

        # If app was provided in constructor, register view with Flask app
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint())

        if is_menu:
            self._add_view_to_menu(view)

    def add_category(self, name, class_name=None, icon_type=None, icon_value=None):
        """
        Add a category of a given name

        :param name:
            The name of the new menu category.
        :param class_name:
            The class name for the new menu category.
        :param icon_type:
            The icon name for the new menu category.
        :param icon_value:
            The icon value for the new menu category.
        """
        cat_text = name

        category = self.get_category_menu_item(name)
        if category:
            return

        category = MenuCategory(
            name, class_name=class_name, icon_type=icon_type, icon_value=icon_value
        )
        self._menu_categories[cat_text] = category
        self._menu.append(category)

    def add_sub_category(self, name, parent_name):
        """
        Add a category of a given name underneath
        the category with parent_name.

        :param name:
            The name of the new menu category.
        :param parent_name:
            The name of a parent_name category
        """

        category = self.get_category_menu_item(name)
        parent = self.get_category_menu_item(parent_name)
        if category is None and parent is not None:
            category = SubMenuCategory(name)
            self._menu_categories[name] = category
            parent.add_child(category)

    def add_link(self, link):
        """
        Add link to menu links collection.

        :param link:
            Link to add.
        """
        if link.category:
            self.add_menu_item(link, link.category)
        else:
            self._menu_links.append(link)

    def add_links(self, *args):
        """
        Add one or more links to the menu links collection.

        Examples::

            admin.add_links(link1)
            admin.add_links(link1, link2, link3, link4)
            admin.add_links(*my_list)

        :param args:
            Argument list including the links to add.
        """
        for link in args:
            self.add_link(link)

    def add_menu_item(self, menu_item, target_category=None):
        """
        Add menu item to menu tree hierarchy.

        :param menu_item:
            MenuItem class instance
        :param target_category:
            Target category name
        """
        if target_category:
            category = self._menu_categories.get(target_category)
            # create a new menu category if one does not exist already
            if category is None:
                category = MenuCategory(target_category)
                category.class_name = self.category_icon_classes.get(target_category)
                self._menu_categories[target_category] = category
                self._menu.append(category)
            category.add_child(menu_item)
        else:
            self._menu.append(menu_item)

    def _add_view_to_menu(self, view):
        """
        Add a view to the menu tree

        :param view:
            View to add
        """
        self.add_menu_item(MenuView(view.name, view), view.category)

    def get_category_menu_item(self, name):
        return self._menu_categories.get(name)

    def get_url(self, endpoint, **kwargs):
        """
        Generate URL for the endpoint. If you want to customize URL generation
        logic (persist some query string argument, for example), this is
        right place to do it.

        :param endpoint:
            Flask endpoint name
        :param kwargs:
            Arguments for `url_for`
        """
        return url_for(endpoint, **kwargs)

    def render(self, template, **kwargs):
        """
        Render template

        :param template:
            Template path to render
        :param kwargs:
            Template arguments
        """
        # Store self as admin
        kwargs["admin"] = self
        # Expose get_url helper
        kwargs["get_url"] = self.get_url

        return render_template(template, **kwargs)

    def init_app(self, app):
        """
        Register all views with the Flask application.

        :param app:
            Flask application instance
        """
        self.app = app
        self._init_extension()

        # Register views
        for view in self._views:
            app.register_blueprint(view.create_blueprint())

    def _init_extension(self):
        if not hasattr(self.app, "extensions"):
            self.app.extensions = dict()

        admins = self.app.extensions.get("admin", [])

        for p in admins:
            if p.endpoint == self.endpoint:
                raise Exception(
                    "Cannot have two Admin() instances with same endpoint name."
                )

            if p.url == self.url:
                raise Exception("Cannot assign two Admin() instances with same URL.")

        admins.append(self)
        self.app.extensions["admin"] = admins

    def menu(self):
        """
        Return the menu hierarchy.
        """
        return self._menu

    def menu_links(self):
        """
        Return menu links.
        """
        return self._menu_links
