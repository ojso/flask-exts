from abc import ABC, abstractmethod


class Authorizer(ABC):
    root_rolename = "admin"
    root_roleid = None

    @abstractmethod
    def allow(self, user, resource, method): ...

    def set_root_roleid(self, id):
        self.root_roleid = id

    def set_root_rolename(self, name):
        self.root_rolename = name

    def is_root_user(self, user=None):
        if hasattr(user, "get_roles"):
            if self.root_rolename in user.get_roles():
                 return True
        return False
