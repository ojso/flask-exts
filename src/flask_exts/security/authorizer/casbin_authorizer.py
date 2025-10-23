import os.path
from casbin.model import Model
from casbin import Enforcer

from .base import Authorizer
from .sqlalchemy_adapter import SqlalchemyAdapter

CASBIN_RBAC_MODEL = """
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
"""


def casbin_prefix_user(user_id):
    return f"user:{user_id}"


def casbin_prefix_role(role_name):
    return f"role:{role_name}"


class CasbinAuthorizer(Authorizer):
    """
    Casbin Enforce decorator
    """

    m = None
    e = None

    def __init__(self, app=None, adapter=None, watcher=None):
        """
        Args:
            app: Flask App object to get Casbin Model
            adapter: Casbin Adapter
        """
        self.app = app
        self.adapter = adapter or SqlalchemyAdapter()
        self.watcher = watcher
        self._owner_loader = None
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app):
        self.app = app
        m = Model()
        if app.config.get("CASBIN_MODEL", None) is not None:
            m_path = os.path.join(app.instance_path, app.config.get("CASBIN_MODEL"))
            m.load_model(m_path)
        else:
            m.load_model_from_text(CASBIN_RBAC_MODEL)
        self.m = m

    def allow(self, user, obj, act):
        e = self.get_casbin_enforcer()
        sub = casbin_prefix_user(user.id)
        access = e.enforce(sub, obj, act)
        if access:
            return access
        if hasattr(user, "get_roles"):
            for r in user.get_roles():
                sub = casbin_prefix_role(r)
                if e.enforce(sub, obj, act):
                    return True
        return False

    def has_role(self, user, role):
        e = self.get_casbin_enforcer()
        if hasattr(user, "get_roles"):
            user_roles = user.get_roles()
            if role in user_roles:
                return True
            rm = e.get_role_manager()
            for r in user_roles:
                sub = casbin_prefix_role(r)
                if rm.has_link(sub, casbin_prefix_role(role)):
                    return True
        return False

    def get_casbin_enforcer(self):
        if self.e is None:
            self.e = Enforcer(self.m, self.adapter)
            if self.watcher:
                self.e.set_watcher(self.watcher)
        if self.e.watcher and self.e.watcher.should_reload():
            self.e.watcher.update_callback()
        return self.e

    def set_watcher(self, watcher):
        """
        Set the watcher to use with the underlying casbin enforcer
        Args:
            watcher (object):
        Returns:
            None
        """
        self.watcher = watcher
