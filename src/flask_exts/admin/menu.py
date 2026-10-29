from flask import url_for


class BaseMenu:
    """
    Base menu item
    """

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.parent = None
        self._children = []
        self._url = None
        self._url_cached = False

    def add_child(self, child):
        if child.parent is not None:
            raise ValueError("menu item is already assigned to some parent")
        child.parent = self
        self._children.append(child)

    def get_url(self):
        if self._url_cached:
            return self._url

    def is_category(self):
        return False

    def is_active(self, view):
        return False

    def is_accessible(self):
        return True

    def get_children(self):
        return [c for c in self._children if c.is_accessible()]


class MenuCategory(BaseMenu):
    """
    Menu category item.
    """

    def __init__(self, name):
        super().__init__(name, "category")

    def is_category(self):
        return True

    def is_active(self, view):
        for c in self._children:
            if c.is_active(view):
                return True
        return False

    def is_accessible(self):
        for c in self._children:
            if c.is_accessible():
                return True
        return False


class MenuView(BaseMenu):
    """
    Admin view menu item
    """

    def __init__(self, name, view):
        super().__init__(name, "view")
        self._view = view

    def get_url(self):
        if self._url_cached:
            return self._url
        else:
            self._url = url_for(f"{self._view.endpoint}.{self._view._default_view}")
            self._url_cached = True
            return self._url

    def is_active(self, view):
        return view == self._view

    def is_accessible(self):
        return self._view.is_accessible()


class MenuEndpoint(BaseMenu):
    """
    Link item
    """

    def __init__(self, name, endpoint):
        super().__init__(name, "endpoint")
        self.endpoint = endpoint

    def get_url(self):
        if self._url_cached:
            return self._url
        else:
            self._url = url_for(self.endpoint)
            self._url_cached = True
            return self._url


class MenuLink(BaseMenu):
    """
    Link item
    """

    def __init__(self, name, url):
        super().__init__(name, "link")
        self._url = url


class Menu:
    def __init__(self, admin):
        self.admin = admin
        self._menu = []

    def get_menus(self):
        """
        Return the menu hierarchy.
        """
        return self._menu

    def add_menu_item(
        self, menu_item: BaseMenu, target_category: BaseMenu | None = None
    ) -> BaseMenu:
        """
        Add menu item to menu tree hierarchy.

        Args:
            menu_item:
                MenuItem class instance
            target_category:
                Target category name
        """
        if target_category is None:
            self._menu.append(menu_item)
        else:
            target_category.add_child(menu_item)

    def add_view(self, view, category=None):
        """
        Add a view to the menu tree

        Args:
            view:
                View to add
        """
        self.add_menu_item(MenuView(view.name, view), category)

    def add_category(self, name):
        """
        Add a category of a given name

        Args:
            name:
                The name of the new menu category.
        """
        category = MenuCategory(name)
        self.add_menu_item(category)
        return category
