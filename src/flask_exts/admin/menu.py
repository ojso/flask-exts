from flask import url_for


class BaseMenu:
    """
    Base menu item
    """

    def __init__(
        self, name, class_name=None, icon_type=None, icon_value=None, target=None
    ):
        self.name = name
        self.class_name = class_name if class_name is not None else ""
        self.icon_type = icon_type
        self.icon_value = icon_value
        self.target = target

        self.parent = None
        self._children = []

    def add_child(self, child):
        if child.parent is not None:
            raise Exception("menu item is already assigned to some parent")
        child.parent = self
        self._children.append(child)

    def get_url(self):
        raise NotImplementedError()

    def get_class_name(self):
        return self.class_name

    def get_icon_type(self):
        return self.icon_type

    def get_icon_value(self):
        return self.icon_value

    def is_category(self):
        return False

    def is_active(self, view):
        for c in self._children:
            if c.is_active(view):
                return True
        return False

    def is_accessible(self):
        return True

    def get_children(self):
        return [c for c in self._children if c.is_accessible()]


class MenuCategory(BaseMenu):
    """
    Menu category item.
    """

    def get_url(self):
        return None

    def is_category(self):
        return True

    def is_accessible(self):
        for c in self._children:
            if c.is_accessible():
                return True

        return False


class MenuView(BaseMenu):
    """
    Admin view menu item
    """

    def __init__(self, name, view=None, cache=True):
        super().__init__(
            name,
            class_name=view.menu_class_name,
            icon_type=view.menu_icon_type,
            icon_value=view.menu_icon_value,
        )

        self._view = view
        self._cache = cache
        self._cached_url = None

        view.menu = self

    def get_url(self):
        if self._view is None:
            return None
        if self._view._default_view is None:
            return None
        if self._cached_url:
            return self._cached_url

        url = url_for("%s.%s" % (self._view.endpoint, self._view._default_view))

        if self._cache:
            self._cached_url = url

        return url

    def is_active(self, view):
        if view == self._view:
            return True

        return super().is_active(view)

    def is_accessible(self):
        if self._view is None:
            return False

        return self._view.is_accessible()


class MenuLink(BaseMenu):
    """
    Link item
    """

    def __init__(
        self,
        name,
        url=None,
        endpoint=None,
        category=None,
        class_name=None,
        icon_type=None,
        icon_value=None,
        target=None,
    ):
        super().__init__(name, class_name, icon_type, icon_value, target)
        self.category = category
        self.url = url
        self.endpoint = endpoint

    def get_url(self):
        return self.url or url_for(self.endpoint)


class SubMenuCategory(MenuCategory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name += " dropdown-submenu dropright"


class Menu:
    def __init__(self, admin, category_icon_classes=None):
        """_summary_

        :param category_icon_classes: _description_, defaults to None
            A dict of category names as keys and html classes as values to be added to menu category icons.
            Example: {'Favorites': 'bi-star'}
        """
        self.admin = admin
        self._menu = []
        self._menu_links = []
        self._menu_categories = dict()
        self.category_icon_classes = category_icon_classes or dict()

    def menus(self):
        """
        Return the menu hierarchy.
        """
        return self._menu

    def menu_links(self):
        """
        Return menu links.
        """
        return self._menu_links

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

    def get_category_menu_item(self, name):
        return self._menu_categories.get(name)

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

    def add_view(self, view, category=None):
        """
        Add a view to the menu tree

        :param view:
            View to add
        """
        self.add_menu_item(MenuView(view.name, view), category)

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
