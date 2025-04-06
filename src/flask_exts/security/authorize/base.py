from abc import ABC, abstractmethod


class BaseAuthorizer(ABC):
    root_rolename = "admin"
    root_roleid = None

    @abstractmethod
    def allow(self, user, resource, method): ...

    def set_root_roleid(self, id):
        self.root_roleid = id

    def set_root_rolename(self, name):
        self.root_rolename = name

    def is_root_user(self, user=None):
        if hasattr(user, "roles"):
            for r in user.roles:
                if r.name == self.root_rolename:
                    return True
        return False
